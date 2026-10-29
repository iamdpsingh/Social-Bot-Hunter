"""Validate and normalise raw rows into typed records.

Rules:
* Nothing is silently dropped. Every rejected row becomes a ``QuarantinedRecord`` with
  machine-readable reasons; exact duplicates are recorded too (kind='duplicate').
* Missing is not zero. Blank cells become ``None``.
* Output lists are sorted by grain key so that batch offsets are stable across restarts.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from sbh.config import ImportConfig
from sbh.contracts.platforms import PLATFORM_VALUES
from sbh.ingestion import fingerprint
from sbh.schemas.io import EXTRA_KEY, RawDataset, RawRow
from sbh.schemas.records import (
    SCHEMA_VERSION,
    AccountObservationRecord,
    CollectionMethod,
    Completeness,
    ContentRecord,
    CoverageDeclaration,
    ListKind,
    Manifest,
    QuarantinedRecord,
    RelationshipRecord,
    RelationshipType,
    VerificationStatus,
)
from sbh.shared import jsonutil
from sbh.shared.errors import SchemaIncompatibleError
from sbh.shared.safety import clean_text
from sbh.shared.timeutil import parse_timestamp, utcnow

_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.:\-]+$")
_TRUE = {"true", "t", "yes", "y", "1"}
_FALSE = {"false", "f", "no", "n", "0"}


# --------------------------------------------------------------------------- manifest

def parse_manifest(raw: dict[str, Any], cfg: ImportConfig, now: datetime | None = None) -> Manifest:
    problems: list[str] = []
    now = now or utcnow()

    def need_str(key: str, max_len: int = 500) -> str:
        v = raw.get(key)
        if not isinstance(v, str) or not v.strip():
            problems.append(f"manifest.{key}: required non-empty string")
            return ""
        try:
            return clean_text(v, max_len)
        except ValueError as exc:
            problems.append(f"manifest.{key}: {exc}")
            return ""

    version = need_str("schema_version", 20)
    if version and version.split(".")[0] != SCHEMA_VERSION.split(".")[0]:
        raise SchemaIncompatibleError(
            f"unsupported schema_version {version!r}; this build reads {SCHEMA_VERSION}.x"
        )
    name = need_str("dataset_name", 200)
    source = need_str("source_description", 1000)
    platform = need_str("platform", 20).casefold()
    if platform and platform not in PLATFORM_VALUES:
        problems.append(f"manifest.platform: {platform!r} not one of {list(PLATFORM_VALUES)}")
    method_raw = need_str("collection_method", 60)
    method: CollectionMethod | None = None
    if method_raw:
        try:
            method = CollectionMethod(method_raw)
        except ValueError:
            problems.append(
                f"manifest.collection_method: {method_raw!r} not one of "
                f"{[m.value for m in CollectionMethod]}"
            )
    collected: datetime | None = None
    try:
        collected = parse_timestamp(raw.get("collected_at"))
        if collected > now + timedelta(seconds=cfg.future_skew_seconds):
            problems.append("manifest.collected_at: is in the future")
    except ValueError as exc:
        problems.append(f"manifest.collected_at: {exc}")

    cov = raw.get("relationship_coverage") or {}
    default = Completeness.UNKNOWN
    overrides: list[CoverageDeclaration] = []
    if not isinstance(cov, dict):
        problems.append("manifest.relationship_coverage: expected an object")
    else:
        try:
            default = Completeness(cov.get("default", "unknown"))
        except ValueError:
            problems.append("manifest.relationship_coverage.default: invalid value")
        seen: set[tuple[str, str]] = set()
        for i, o in enumerate(cov.get("overrides") or []):
            try:
                acct = str(o["platform_account_id"]).strip()
                kind = ListKind(o["list_kind"])
                comp = Completeness(o["completeness"])
                exp = o.get("expected_count")
                if exp is not None and (isinstance(exp, bool) or int(exp) != exp or int(exp) < 0):
                    raise ValueError("expected_count must be a non-negative integer")
                if not _ID_PATTERN.match(acct) or len(acct) > cfg.max_identifier_length:
                    raise ValueError("invalid platform_account_id")
                if (acct, kind.value) in seen:
                    problems.append(
                        f"manifest.relationship_coverage.overrides[{i}]: conflicting duplicate "
                        f"declaration for {acct}/{kind.value}"
                    )
                seen.add((acct, kind.value))
                overrides.append(
                    CoverageDeclaration(acct, kind, comp, None if exp is None else int(exp))
                )
            except (KeyError, ValueError, TypeError) as exc:
                problems.append(f"manifest.relationship_coverage.overrides[{i}]: {exc}")

    if problems:
        raise SchemaIncompatibleError("; ".join(problems))
    assert collected is not None and method is not None
    notes = raw.get("notes")
    return Manifest(
        schema_version=version, dataset_name=name, platform=platform, collected_at=collected,
        source_description=source, collection_method=method, coverage_default=default,
        coverage_overrides=tuple(overrides), notes=notes if isinstance(notes, str) else None,
    )


# --------------------------------------------------------------------------- row parsing

class _RowReader:
    """Collects every problem in a row instead of stopping at the first."""

    def __init__(self, data: dict[str, Any], cfg: ImportConfig) -> None:
        self.d = data
        self.cfg = cfg
        self.reasons: list[str] = []

    @staticmethod
    def _blank(v: Any) -> bool:
        return v is None or (isinstance(v, str) and not v.strip())

    def req_id(self, key: str) -> str:
        v = self.d.get(key)
        if self._blank(v):
            self.reasons.append(f"missing_required:{key}")
            return ""
        text = str(v).strip()
        if len(text) > self.cfg.max_identifier_length or not _ID_PATTERN.match(text):
            self.reasons.append(f"invalid_identifier:{key}")
            return ""
        return text

    def opt_str(self, key: str, max_len: int) -> str | None:
        v = self.d.get(key)
        if self._blank(v):
            return None
        try:
            return clean_text(str(v), max_len)
        except ValueError:
            self.reasons.append(f"invalid_text:{key}")
            return None

    def opt_int(self, key: str) -> int | None:
        v = self.d.get(key)
        if self._blank(v):
            return None
        if isinstance(v, bool):
            self.reasons.append(f"invalid_integer:{key}")
            return None
        try:
            if isinstance(v, float):
                if not v.is_integer():
                    raise ValueError
                n = int(v)
            else:
                n = int(str(v).strip())
        except ValueError:
            self.reasons.append(f"invalid_integer:{key}")
            return None
        if n < 0:
            self.reasons.append(f"negative_count:{key}")
            return None
        return n

    def opt_bool(self, key: str) -> bool | None:
        v = self.d.get(key)
        if self._blank(v):
            return None
        if isinstance(v, bool):
            return v
        s = str(v).strip().casefold()
        if s in _TRUE:
            return True
        if s in _FALSE:
            return False
        self.reasons.append(f"invalid_boolean:{key}")
        return None

    def ts(self, key: str, required: bool) -> datetime | None:
        v = self.d.get(key)
        if self._blank(v):
            if required:
                self.reasons.append(f"missing_required:{key}")
            return None
        try:
            return parse_timestamp(v)
        except ValueError as exc:
            self.reasons.append(f"invalid_timestamp:{key}:{exc}")
            return None

    def platform(self, expected: str) -> str:
        v = self.d.get("platform")
        if self._blank(v):
            self.reasons.append("missing_required:platform")
            return ""
        p = str(v).strip().casefold()
        if p not in PLATFORM_VALUES:
            self.reasons.append("invalid_platform")
            return ""
        if p != expected:
            self.reasons.append("platform_mismatch")
            return ""
        return p


@dataclass
class ValidationOutcome:
    accounts: list[AccountObservationRecord] = field(default_factory=list)
    relationships: list[RelationshipRecord] = field(default_factory=list)
    content: list[ContentRecord] = field(default_factory=list)
    quarantined: list[QuarantinedRecord] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)
    # (platform_account_id, list_kind) -> declaration actually in force (after consistency checks)
    coverage_overrides: dict[tuple[str, str], CoverageDeclaration] = field(default_factory=dict)

    @property
    def rejected_count(self) -> int:
        return sum(1 for q in self.quarantined if q.kind == "invalid")


def _safe_raw(row: RawRow) -> dict[str, object]:
    """Keep quarantined payloads small and free of free-text post bodies."""
    out: dict[str, object] = {}
    for k, v in row.data.items():
        if k == "text":
            out[k] = f"<{len(str(v))} chars omitted>"
        else:
            out[k] = v if isinstance(v, (int, float, bool, type(None))) else str(v)[:200]
    return out


def validate_dataset(raw: RawDataset, manifest: Manifest, cfg: ImportConfig) -> ValidationOutcome:
    out = ValidationOutcome(warnings=list(raw.warnings))
    skew = timedelta(seconds=cfg.future_skew_seconds)
    horizon = manifest.collected_at + skew
    plat = manifest.platform

    def reject(entity: str, row: RawRow, reasons: list[str]) -> None:
        out.quarantined.append(
            QuarantinedRecord(entity, row.ref, "invalid", tuple(reasons), _safe_raw(row))
        )

    def duplicate(entity: str, row: RawRow, exact: bool) -> None:
        kind, reason = ("duplicate", "duplicate_in_file") if exact else ("invalid", "conflicting_duplicate")
        out.quarantined.append(QuarantinedRecord(entity, row.ref, kind, (reason,), _safe_raw(row)))

    # ---- accounts
    seen_acc: dict[tuple[str, datetime], AccountObservationRecord] = {}
    for row in raw.rows["accounts"]:
        if EXTRA_KEY in row.data:
            reject("account", row, ["malformed_row"])
            continue
        r = _RowReader(row.data, cfg)
        p = r.platform(plat)
        acct = r.req_id("platform_account_id")
        observed = r.ts("observed_at", True)
        username = r.opt_str("username", cfg.max_username_length)
        if username and username.startswith("@"):
            username = username[1:] or None
        display = r.opt_str("display_name", cfg.max_display_name_length)
        followers, following, posts = r.opt_int("follower_count"), r.opt_int("following_count"), r.opt_int("post_count")
        has_bio, bio_len = r.opt_bool("has_bio"), r.opt_int("bio_length")
        has_img, has_disp = r.opt_bool("has_profile_image"), r.opt_bool("has_display_name")
        created = r.ts("account_created_at", False)
        verified, private = r.opt_bool("is_verified"), r.opt_bool("is_private")
        if observed and observed > horizon:
            r.reasons.append("future_timestamp:observed_at")
        if observed and created and created > observed:
            r.reasons.append("inconsistent:account_created_after_observation")
        if has_bio is False and bio_len:
            r.reasons.append("inconsistent:has_bio_false_with_bio_length")
        if r.reasons:
            reject("account", row, r.reasons)
            continue
        assert observed is not None
        if has_bio is None and bio_len is not None:
            has_bio = bio_len > 0
        if has_disp is None and display:
            has_disp = True
        payload = jsonutil.sha256_hex(jsonutil.dumps({k: v for k, v in row.data.items()}))
        rec = AccountObservationRecord(
            platform=p, platform_account_id=acct, observed_at=observed, username=username,
            display_name=display, follower_count=followers, following_count=following,
            post_count=posts, has_bio=has_bio, bio_length=bio_len, has_profile_image=has_img,
            has_display_name=has_disp, account_created_at=created, is_verified=verified,
            is_private=private, source_ref=row.ref, payload_sha256=payload,
        )
        key = (acct, observed)
        if key in seen_acc:
            duplicate("account", row, seen_acc[key].comparable() == rec.comparable())
        else:
            seen_acc[key] = rec

    # ---- relationships
    seen_rel: dict[tuple[str, str, str], RelationshipRecord] = {}
    for row in raw.rows["relationships"]:
        if EXTRA_KEY in row.data:
            reject("relationship", row, ["malformed_row"])
            continue
        r = _RowReader(row.data, cfg)
        p = r.platform(plat)
        src, dst = r.req_id("source_account_id"), r.req_id("target_account_id")
        observed = r.ts("observed_at", True)
        rtype_raw = row.data.get("relationship_type")
        rtype = None
        if r._blank(rtype_raw):
            r.reasons.append("missing_required:relationship_type")
        else:
            try:
                rtype = RelationshipType(str(rtype_raw).strip().casefold())
            except ValueError:
                r.reasons.append("invalid_enum:relationship_type")
        vs_raw = row.data.get("verification_status")
        vstatus = VerificationStatus.UNVERIFIED
        if not r._blank(vs_raw):
            try:
                vstatus = VerificationStatus(str(vs_raw).strip().casefold())
            except ValueError:
                r.reasons.append("invalid_enum:verification_status")
        if src and dst and src == dst:
            r.reasons.append("self_relationship")
        if observed and observed > horizon:
            r.reasons.append("future_timestamp:observed_at")
        if r.reasons:
            reject("relationship", row, r.reasons)
            continue
        assert observed is not None and rtype is not None
        rec = RelationshipRecord(p, src, dst, rtype, observed, vstatus, row.ref)
        key3 = (src, dst, rtype.value)
        if key3 in seen_rel:
            duplicate("relationship", row, seen_rel[key3].comparable() == rec.comparable())
        else:
            seen_rel[key3] = rec

    # ---- content
    seen_con: dict[str, ContentRecord] = {}
    for row in raw.rows["content"]:
        if EXTRA_KEY in row.data:
            reject("content", row, ["malformed_row"])
            continue
        r = _RowReader(row.data, cfg)
        p = r.platform(plat)
        cid, author = r.req_id("platform_content_id"), r.req_id("author_account_id")
        published = r.ts("published_at", True)
        likes, replies, shares = r.opt_int("like_count"), r.opt_int("reply_count"), r.opt_int("share_count")
        provided_hash = r.opt_str("content_hash", 128)
        text_raw = row.data.get("text")
        chash, sim, tlen = provided_hash, None, None
        if not r._blank(text_raw):
            text = str(text_raw)
            if len(text) > 100_000:
                r.reasons.append("invalid_text:text")
            else:
                # Computed fingerprints win over a supplied hash so a dataset cannot mix schemes.
                chash, sim, tlen = fingerprint.content_hash(text), fingerprint.simhash64(text), len(text)
        if published and published > horizon:
            r.reasons.append("future_timestamp:published_at")
        if r.reasons:
            reject("content", row, r.reasons)
            continue
        assert published is not None
        rec = ContentRecord(p, cid, author, published, chash, sim, tlen, likes, replies, shares, row.ref)
        if cid in seen_con:
            duplicate("content", row, seen_con[cid].comparable() == rec.comparable())
        else:
            seen_con[cid] = rec

    out.accounts = sorted(seen_acc.values(), key=lambda a: (a.platform_account_id, a.observed_at))
    out.relationships = sorted(
        seen_rel.values(), key=lambda e: (e.source_account_id, e.target_account_id, e.relationship_type.value)
    )
    out.content = sorted(seen_con.values(), key=lambda c: c.platform_content_id)
    _derive_stats_and_warnings(out, manifest, cfg)
    return out


# --------------------------------------------------------------------------- quality checks

def _derive_stats_and_warnings(out: ValidationOutcome, manifest: Manifest, cfg: ImportConfig) -> None:
    raw_counts = Counter(q.entity for q in out.quarantined)
    out.stats = {
        "accepted": {
            "accounts": len(out.accounts), "relationships": len(out.relationships),
            "content": len(out.content),
        },
        "rejected": {e: sum(1 for q in out.quarantined if q.entity == e and q.kind == "invalid")
                     for e in ("account", "relationship", "content")},
        "exact_duplicates": {e: sum(1 for q in out.quarantined if q.entity == e and q.kind == "duplicate")
                             for e in ("account", "relationship", "content")},
        "quarantined_total": sum(raw_counts.values()),
    }

    # Missingness patterns across optional account fields (only meaningful with enough rows).
    n = len(out.accounts)
    if n >= 20:
        optional = ("username", "follower_count", "following_count", "post_count", "has_bio",
                    "has_profile_image", "account_created_at")
        missing = {f: sum(1 for a in out.accounts if getattr(a, f) is None) / n for f in optional}
        out.stats["missing_fraction"] = missing
        for f, frac in missing.items():
            if frac >= cfg.missing_field_warn_fraction:
                out.warnings.append(
                    f"accounts.{f} is missing in {frac:.0%} of observations; dependent features will be unavailable"
                )

    # Freshness relative to when the data was collected.
    stale_cut = manifest.collected_at - timedelta(days=cfg.stale_observation_days)
    stale = sum(1 for a in out.accounts if a.observed_at < stale_cut)
    if stale:
        out.warnings.append(
            f"{stale} account observations are older than {cfg.stale_observation_days} days at collection time"
        )
    out.stats["stale_observations"] = stale

    # Referential integrity: endpoints without an observation become stub accounts.
    known = {a.platform_account_id for a in out.accounts}
    endpoints = {e.source_account_id for e in out.relationships} | {e.target_account_id for e in out.relationships}
    authors = {c.author_account_id for c in out.content}
    stubs = (endpoints | authors) - known
    out.stats["stub_accounts"] = len(stubs)
    if stubs:
        out.warnings.append(
            f"{len(stubs)} accounts appear only as relationship endpoints or content authors; "
            "they have no profile observation and will usually lack enough evidence for a score"
        )

    # Pagination/completeness consistency: a 'complete' list must match its expected count.
    following = Counter(e.source_account_id for e in out.relationships)
    followers = Counter(e.target_account_id for e in out.relationships)
    for decl in manifest.coverage_overrides:
        observed = (following if decl.list_kind is ListKind.FOLLOWING else followers)[decl.platform_account_id]
        effective = decl
        if decl.expected_count is not None and decl.completeness is Completeness.COMPLETE \
                and observed != decl.expected_count:
            out.warnings.append(
                f"{decl.platform_account_id}/{decl.list_kind.value}: declared complete with expected "
                f"{decl.expected_count} but {observed} observed; downgraded to partial"
            )
            effective = CoverageDeclaration(decl.platform_account_id, decl.list_kind,
                                            Completeness.PARTIAL, decl.expected_count)
        out.coverage_overrides[(decl.platform_account_id, decl.list_kind.value)] = effective

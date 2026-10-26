"""Read a dataset from disk into raw rows. No interpretation happens here beyond structure.

Two layouts are accepted:

* a directory with ``manifest.json`` plus any of ``accounts.csv``, ``relationships.csv``,
  ``content.csv``;
* a single ``.json`` bundle: ``{"manifest": {...}, "accounts": [...], "relationships": [...],
  "content": [...]}``.

The SHA-256 over the input is the idempotency key: importing the same bytes twice is a no-op.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sbh.config import ImportConfig
from sbh.shared.errors import ImportLimitError, SchemaIncompatibleError

EXTRA_KEY = "__extra__"

REQUIRED_COLUMNS: dict[str, tuple[str, ...]] = {
    "accounts": ("platform", "platform_account_id", "observed_at"),
    "relationships": (
        "platform", "source_account_id", "target_account_id", "relationship_type", "observed_at",
    ),
    "content": ("platform", "platform_content_id", "author_account_id", "published_at"),
}
OPTIONAL_COLUMNS: dict[str, tuple[str, ...]] = {
    "accounts": (
        "username", "display_name", "follower_count", "following_count", "post_count",
        "has_bio", "bio_length", "has_profile_image", "has_display_name",
        "account_created_at", "is_verified", "is_private",
    ),
    "relationships": ("verification_status",),
    "content": ("content_hash", "text", "like_count", "reply_count", "share_count"),
}
ENTITIES = ("accounts", "relationships", "content")


@dataclass
class RawRow:
    ref: str
    data: dict[str, Any]


@dataclass
class RawDataset:
    source_name: str
    sha256: str
    manifest: dict[str, Any]
    rows: dict[str, list[RawRow]] = field(default_factory=lambda: {e: [] for e in ENTITIES})
    warnings: list[str] = field(default_factory=list)


def _read_csv(name: str, raw: bytes, cfg: ImportConfig, ds: RawDataset) -> None:
    entity = name.removesuffix(".csv")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise SchemaIncompatibleError(f"{name}: not valid UTF-8") from exc
    if "\x00" in text:
        raise SchemaIncompatibleError(f"{name}: contains NUL bytes")
    reader = csv.DictReader(io.StringIO(text), restkey=EXTRA_KEY)
    headers = [h.strip() for h in (reader.fieldnames or [])]
    reader.fieldnames = headers
    missing = [c for c in REQUIRED_COLUMNS[entity] if c not in headers]
    if missing:
        raise SchemaIncompatibleError(f"{name}: missing required columns {missing}")
    known = set(REQUIRED_COLUMNS[entity]) | set(OPTIONAL_COLUMNS[entity])
    unknown = sorted(h for h in headers if h and h not in known)
    if unknown:
        ds.warnings.append(f"{name}: unknown columns ignored: {unknown}")
    try:
        for i, row in enumerate(reader, start=2):  # row 1 is the header
            if len(ds.rows[entity]) >= cfg.max_records_per_file:
                raise ImportLimitError(f"{name}: more than {cfg.max_records_per_file} rows")
            data = {k: v for k, v in row.items() if k is not None and (k in known or k == EXTRA_KEY)}
            ds.rows[entity].append(RawRow(ref=f"{name}:{i}", data=data))
    except csv.Error as exc:
        raise SchemaIncompatibleError(f"{name}: malformed CSV ({exc})") from exc


def _read_bundle(raw: bytes, cfg: ImportConfig, ds: RawDataset) -> None:
    try:
        doc = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SchemaIncompatibleError(f"bundle is not valid UTF-8 JSON: {exc}") from exc
    if not isinstance(doc, dict) or not isinstance(doc.get("manifest"), dict):
        raise SchemaIncompatibleError("bundle must be an object with a 'manifest' object")
    ds.manifest = doc["manifest"]
    extra_top = sorted(set(doc) - {"manifest", *ENTITIES})
    if extra_top:
        ds.warnings.append(f"bundle: unknown top-level keys ignored: {extra_top}")
    for entity in ENTITIES:
        rows = doc.get(entity, [])
        if not isinstance(rows, list):
            raise SchemaIncompatibleError(f"bundle.{entity}: expected a list")
        if len(rows) > cfg.max_records_per_file:
            raise ImportLimitError(f"bundle.{entity}: more than {cfg.max_records_per_file} rows")
        for i, row in enumerate(rows, start=1):
            if isinstance(row, dict):
                ds.rows[entity].append(RawRow(ref=f"bundle.{entity}[{i}]", data=dict(row)))
            else:
                ds.rows[entity].append(RawRow(ref=f"bundle.{entity}[{i}]", data={EXTRA_KEY: row}))


def load_source(path: str | Path, cfg: ImportConfig) -> RawDataset:
    p = Path(path)
    if not p.exists():
        raise SchemaIncompatibleError(f"source not found: {p}")
    hasher = hashlib.sha256()
    if p.is_dir():
        manifest_path = p / "manifest.json"
        if not manifest_path.is_file():
            raise SchemaIncompatibleError(f"{p}: manifest.json is required")
        files = [n for n in ("manifest.json", "accounts.csv", "relationships.csv", "content.csv")
                 if (p / n).is_file()]
        total = sum((p / n).stat().st_size for n in files)
        if total > cfg.max_file_bytes:
            raise ImportLimitError(f"input is {total} bytes, limit is {cfg.max_file_bytes}")
        ds = RawDataset(source_name=p.name, sha256="", manifest={})
        for n in files:
            raw = (p / n).read_bytes()
            hasher.update(n.encode() + b"\0" + str(len(raw)).encode() + b"\0" + raw)
            if n == "manifest.json":
                try:
                    ds.manifest = json.loads(raw.decode("utf-8-sig"))
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise SchemaIncompatibleError(f"manifest.json is not valid JSON: {exc}") from exc
                if not isinstance(ds.manifest, dict):
                    raise SchemaIncompatibleError("manifest.json must be an object")
            else:
                _read_csv(n, raw, cfg, ds)
        if not any(ds.rows[e] for e in ENTITIES):
            raise SchemaIncompatibleError(f"{p}: no data files found (accounts/relationships/content)")
    else:
        if p.stat().st_size > cfg.max_file_bytes:
            raise ImportLimitError(f"input is {p.stat().st_size} bytes, limit is {cfg.max_file_bytes}")
        raw = p.read_bytes()
        hasher.update(raw)
        ds = RawDataset(source_name=p.name, sha256="", manifest={})
        _read_bundle(raw, cfg, ds)
    ds.sha256 = hasher.hexdigest()
    return ds

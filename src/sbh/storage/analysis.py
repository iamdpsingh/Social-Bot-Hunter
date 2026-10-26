"""Features, model versions, risk assessments, clusters and evidence.

Derived outputs are replaced per (scan, version) inside a transaction, which makes each
analysis stage safe to re-run after a restart.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from sbh.shared import jsonutil
from sbh.shared.errors import ConfigError
from sbh.shared.ids import new_id
from sbh.shared.timeutil import iso_utc, utcnow
from sbh.storage.database import Database


@dataclass(frozen=True)
class FeatureRow:
    account_id: str  # internal id
    name: str
    category: str
    value: float | None
    unavailable_reason: str | None
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AssessmentRow:
    account_id: str  # internal id
    status: str
    score: float | None
    band: str | None
    evidence_coverage: float
    features_available: int
    features_total: int
    contributions: list[dict[str, Any]]
    limitations: list[str]


@dataclass(frozen=True)
class EvidenceRow:
    subject_type: str
    subject_id: str
    evidence_type: str
    summary: str
    details: dict[str, Any]
    source_refs: list[dict[str, str]]


@dataclass(frozen=True)
class ClusterRow:
    members: list[tuple[str, dict[str, Any]]]  # (internal account id, member metrics)
    method: str
    method_version: str
    metrics: dict[str, Any]
    signals: dict[str, Any]
    coverage: dict[str, Any]
    signal_strength: str
    confidence: str
    uncertainty_notes: list[str]
    alternative_explanations: list[str]
    evidence: list[tuple[str, str, dict[str, Any]]]  # (evidence_type, summary, details)
    cluster_id: str = field(default_factory=new_id)


class AnalysisRepository:
    def __init__(self, db: Database, clock: Callable[[], datetime] = utcnow) -> None:
        self.db = db
        self.clock = clock

    # ---- model versions
    def register_model_version(self, *, kind: str, name: str, version: str, config: dict[str, Any],
                               config_sha256: str, feature_schema: dict[str, Any] | None = None) -> str:
        """Idempotent. Reusing a version name with different configuration is an error: the version
        string is what makes a stored score reproducible."""
        existing = self.db.query_one(
            "SELECT id, config_sha256 FROM model_versions WHERE kind = :k AND name = :n AND version = :v",
            {"k": kind, "n": name, "v": version})
        if existing:
            if existing["config_sha256"] != config_sha256:
                raise ConfigError(
                    f"{kind}/{name}/{version} already registered with different configuration; "
                    "bump the version when changing weights or thresholds")
            return str(existing["id"])
        mv = new_id()
        self.db.execute(
            "INSERT INTO model_versions (id, kind, name, version, config, config_sha256, feature_schema, created_at) "
            "VALUES (:id, :k, :n, :v, :c, :h, :fs, :now)",
            {"id": mv, "k": kind, "n": name, "v": version, "c": jsonutil.dumps(config), "h": config_sha256,
             "fs": jsonutil.dumps(feature_schema) if feature_schema is not None else None,
             "now": iso_utc(self.clock())})
        return mv

    # ---- features
    def replace_features(self, scan_id: str, feature_version: str, rows: Sequence[FeatureRow]) -> None:
        now = iso_utc(self.clock())
        with self.db.transaction():
            self.db.execute("DELETE FROM account_features WHERE scan_id = :s AND feature_version = :v",
                            {"s": scan_id, "v": feature_version})
            self.db.executemany(
                "INSERT INTO account_features (id, scan_id, platform_account_id, feature_name, feature_version, "
                "category, value, is_available, unavailable_reason, details, computed_at) "
                "VALUES (:id, :s, :a, :n, :v, :cat, :val, :avail, :why, :d, :now)",
                [{"id": new_id(), "s": scan_id, "a": r.account_id, "n": r.name, "v": feature_version,
                  "cat": r.category, "val": r.value, "avail": r.value is not None,
                  "why": r.unavailable_reason, "d": jsonutil.dumps(r.details), "now": now} for r in rows])

    def load_features(self, scan_id: str, feature_version: str) -> dict[str, dict[str, dict[str, Any]]]:
        """public account id -> feature name -> {value, category, reason, details}."""
        rows = self.db.query_all(
            "SELECT a.platform_account_id AS pid, f.feature_name, f.category, f.value, f.unavailable_reason, "
            "f.details, f.platform_account_id AS internal_id FROM account_features f "
            "JOIN platform_accounts a ON a.id = f.platform_account_id "
            "WHERE f.scan_id = :s AND f.feature_version = :v", {"s": scan_id, "v": feature_version})
        out: dict[str, dict[str, dict[str, Any]]] = {}
        for r in rows:
            out.setdefault(r["pid"], {})[r["feature_name"]] = {
                "value": r["value"], "category": r["category"], "reason": r["unavailable_reason"],
                "details": jsonutil.loads(r["details"]) or {}, "internal_id": r["internal_id"]}
        return out

    # ---- assessments and evidence
    def replace_assessments(self, scan_id: str, model_version_id: str, feature_version: str,
                            rows: Sequence[AssessmentRow]) -> None:
        now = iso_utc(self.clock())
        with self.db.transaction():
            self.db.execute(
                "DELETE FROM risk_assessments WHERE scan_id = :s AND model_version_id = :m AND feature_version = :v",
                {"s": scan_id, "m": model_version_id, "v": feature_version})
            self.db.executemany(
                "INSERT INTO risk_assessments (id, scan_id, platform_account_id, feature_version, model_version_id, "
                "status, score, band, evidence_coverage, features_available, features_total, contributions, "
                "limitations, assessed_at) VALUES (:id, :s, :a, :fv, :m, :st, :score, :band, :cov, :fa, :ft, :c, "
                ":l, :now)",
                [{"id": new_id(), "s": scan_id, "a": r.account_id, "fv": feature_version, "m": model_version_id,
                  "st": r.status, "score": r.score, "band": r.band, "cov": r.evidence_coverage,
                  "fa": r.features_available, "ft": r.features_total, "c": jsonutil.dumps(r.contributions),
                  "l": jsonutil.dumps(r.limitations), "now": now} for r in rows])

    def replace_evidence(self, scan_id: str, subject_type: str, model_version_id: str,
                         rows: Sequence[EvidenceRow]) -> None:
        now = iso_utc(self.clock())
        with self.db.transaction():
            self.db.execute(
                "DELETE FROM evidence_records WHERE scan_id = :s AND subject_type = :t AND model_version_id = :m",
                {"s": scan_id, "t": subject_type, "m": model_version_id})
            self.db.executemany(
                "INSERT INTO evidence_records (id, scan_id, subject_type, subject_id, evidence_type, summary, "
                "details, source_refs, model_version_id, created_at) VALUES (:id, :s, :t, :sid, :et, :sum, :d, "
                ":refs, :m, :now)",
                [{"id": new_id(), "s": scan_id, "t": r.subject_type, "sid": r.subject_id, "et": r.evidence_type,
                  "sum": r.summary, "d": jsonutil.dumps(r.details), "refs": jsonutil.dumps(r.source_refs),
                  "m": model_version_id, "now": now} for r in rows])

    def list_assessments(self, scan_id: str) -> list[dict[str, Any]]:
        rows = self.db.query_all(
            "SELECT r.*, a.platform_account_id AS pid, a.username FROM risk_assessments r "
            "JOIN platform_accounts a ON a.id = r.platform_account_id WHERE r.scan_id = :s "
            "ORDER BY r.score DESC, a.platform_account_id", {"s": scan_id})
        for r in rows:
            r["contributions"] = jsonutil.loads(r["contributions"])
            r["limitations"] = jsonutil.loads(r["limitations"])
        return rows

    def list_evidence(self, scan_id: str, subject_type: str, subject_id: str) -> list[dict[str, Any]]:
        rows = self.db.query_all(
            "SELECT * FROM evidence_records WHERE scan_id = :s AND subject_type = :t AND subject_id = :i "
            "ORDER BY evidence_type, summary", {"s": scan_id, "t": subject_type, "i": subject_id})
        for r in rows:
            r["details"] = jsonutil.loads(r["details"])
            r["source_refs"] = jsonutil.loads(r["source_refs"])
        return rows

    # ---- clusters
    def replace_clusters(self, scan_id: str, model_version_id: str, clusters: Sequence[ClusterRow]) -> None:
        now = iso_utc(self.clock())
        with self.db.transaction():
            old = [r["id"] for r in self.db.query_all(
                "SELECT id FROM network_clusters WHERE scan_id = :s AND model_version_id = :m",
                {"s": scan_id, "m": model_version_id})]
            for cid in old:
                self.db.execute("DELETE FROM cluster_memberships WHERE cluster_id = :c", {"c": cid})
                self.db.execute("DELETE FROM evidence_records WHERE subject_type = 'cluster' AND subject_id = :c",
                                {"c": cid})
                self.db.execute("DELETE FROM network_clusters WHERE id = :c", {"c": cid})
            for c in clusters:
                self.db.execute(
                    "INSERT INTO network_clusters (id, scan_id, model_version_id, method, method_version, "
                    "member_count, metrics, signals, coverage, signal_strength, confidence, uncertainty_notes, "
                    "alternative_explanations, review_status, created_at) VALUES (:id, :s, :m, :meth, :mv, :n, "
                    ":met, :sig, :cov, :ss, :conf, :un, :alt, 'unreviewed', :now)",
                    {"id": c.cluster_id, "s": scan_id, "m": model_version_id, "meth": c.method,
                     "mv": c.method_version, "n": len(c.members), "met": jsonutil.dumps(c.metrics),
                     "sig": jsonutil.dumps(c.signals), "cov": jsonutil.dumps(c.coverage),
                     "ss": c.signal_strength, "conf": c.confidence,
                     "un": jsonutil.dumps(c.uncertainty_notes), "alt": jsonutil.dumps(c.alternative_explanations),
                     "now": now})
                self.db.executemany(
                    "INSERT INTO cluster_memberships (cluster_id, platform_account_id, scan_id, metrics) "
                    "VALUES (:c, :a, :s, :m)",
                    [{"c": c.cluster_id, "a": acc, "s": scan_id, "m": jsonutil.dumps(m)} for acc, m in c.members])
                self.db.executemany(
                    "INSERT INTO evidence_records (id, scan_id, subject_type, subject_id, evidence_type, summary, "
                    "details, source_refs, model_version_id, created_at) VALUES (:id, :s, 'cluster', :sid, :et, "
                    ":sum, :d, '[]', :m, :now)",
                    [{"id": new_id(), "s": scan_id, "sid": c.cluster_id, "et": et, "sum": summ,
                      "d": jsonutil.dumps(det), "m": model_version_id, "now": now} for et, summ, det in c.evidence])

    def list_clusters(self, scan_id: str) -> list[dict[str, Any]]:
        rows = self.db.query_all(
            "SELECT * FROM network_clusters WHERE scan_id = :s ORDER BY member_count DESC, id", {"s": scan_id})
        for r in rows:
            for k in ("metrics", "signals", "coverage", "uncertainty_notes", "alternative_explanations"):
                r[k] = jsonutil.loads(r[k])
            r["members"] = [
                m["pid"] for m in self.db.query_all(
                    "SELECT a.platform_account_id AS pid FROM cluster_memberships m "
                    "JOIN platform_accounts a ON a.id = m.platform_account_id WHERE m.cluster_id = :c "
                    "ORDER BY a.platform_account_id", {"c": r["id"]})]
        return rows

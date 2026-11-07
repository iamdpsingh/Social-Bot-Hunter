"""Deletion and retention.

``delete_scan`` removes everything a scan produced, then removes accounts that no remaining scan
references. The audit trail is kept on purpose: it records *that* a deletion happened, who asked,
and how many rows went, without retaining the deleted content. Model versions are configuration,
not personal data, and are kept.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from sbh.shared.errors import SbhError
from sbh.shared.timeutil import iso_utc, utcnow
from sbh.storage.database import Database
from sbh.storage.scans import ScanRepository

# Child tables first so foreign keys are satisfied at every step.
_SCAN_TABLES = (
    ("cluster_memberships", "scan_id"),
    ("evidence_records", "scan_id"),
    ("network_clusters", "scan_id"),
    ("risk_assessments", "scan_id"),
    ("account_features", "scan_id"),
    ("relationship_list_coverage", "scan_id"),
    ("relationship_edges", "scan_id"),
    ("content_observations", "scan_id"),
    ("account_observations", "scan_id"),
    ("quarantined_records", "scan_id"),
    ("scan_checkpoints", "scan_id"),
    ("dataset_imports", "scan_id"),
)

_ORPHAN_ACCOUNTS = (
    "DELETE FROM platform_accounts WHERE id NOT IN ("
    "SELECT platform_account_id FROM account_observations "
    "UNION SELECT source_account_id FROM relationship_edges "
    "UNION SELECT target_account_id FROM relationship_edges "
    "UNION SELECT author_account_id FROM content_observations "
    "UNION SELECT platform_account_id FROM relationship_list_coverage "
    "UNION SELECT platform_account_id FROM account_features "
    "UNION SELECT platform_account_id FROM risk_assessments "
    "UNION SELECT platform_account_id FROM cluster_memberships)"
)


def delete_scan(
    db: Database, scan_id: str, actor: str, clock: Callable[[], datetime] = utcnow
) -> dict[str, Any]:
    """Delete one scan and its derived data. Refuses to touch a scan that is still running."""
    scans = ScanRepository(db, clock)
    scan = scans.get_scan(scan_id)
    if scan is None:
        raise SbhError(f"no such scan: {scan_id}")
    if scan["status"] == "running":
        raise SbhError(f"scan {scan_id} is running; cancel or wait before deleting")
    counts: dict[str, int] = {}
    with db.transaction():
        for table, col in _SCAN_TABLES:
            counts[table] = db.execute(f"DELETE FROM {table} WHERE {col} = :s", {"s": scan_id})
        counts["scan_jobs"] = db.execute("DELETE FROM scan_jobs WHERE id = :s", {"s": scan_id})
        counts["platform_accounts_orphaned"] = db.execute(_ORPHAN_ACCOUNTS)
        scans.audit(
            actor,
            "scan_deleted",
            "scan",
            scan_id,
            {"platform": scan["platform"], "rows_deleted": counts, "status_was": scan["status"]},
        )
    return counts


def delete_scans_older_than(
    db: Database, days: int, actor: str, clock: Callable[[], datetime] = utcnow
) -> list[str]:
    """Retention sweep: delete finished scans created more than ``days`` days ago."""
    if days < 1:
        raise ValueError("days must be >= 1")
    cutoff = iso_utc(clock() - timedelta(days=days))
    rows = db.query_all(
        "SELECT id FROM scan_jobs WHERE created_at < :c AND status IN ('complete', 'partial', 'failed', 'cancelled') "
        "ORDER BY created_at",
        {"c": cutoff},
    )
    deleted = []
    for r in rows:
        delete_scan(db, r["id"], actor, clock)
        deleted.append(r["id"])
    return deleted


@dataclass(frozen=True)
class RetentionStats:
    total_scans: int
    oldest_scan_at: str | None
    retention_days: int
    expired_scans_count: int
    database_size_bytes: int
    auto_purge_enabled: bool


@dataclass(frozen=True)
class PurgeResult:
    scans_purged: int
    assessments_purged: int
    evidence_purged: int
    dry_run: bool
    purged_at: str


class RetentionManager:
    """Manages investigation data retention and purge lifecycle."""

    def __init__(self, db: Database, default_retention_days: int = 90) -> None:
        self.db = db
        self.default_retention_days = default_retention_days

    def get_stats(self, retention_days: int | None = None) -> RetentionStats:
        days = retention_days if retention_days is not None else self.default_retention_days
        now = datetime.now(UTC)
        cutoff = now - timedelta(days=days)

        scan_count_row = self.db.query_one("SELECT COUNT(*) as count FROM scan_jobs")
        total_scans = int(scan_count_row["count"]) if scan_count_row else 0

        oldest_row = self.db.query_one("SELECT MIN(created_at) as oldest FROM scan_jobs")
        oldest_scan_at = str(oldest_row["oldest"]) if oldest_row and oldest_row["oldest"] else None

        expired_row = self.db.query_one(
            "SELECT COUNT(*) as count FROM scan_jobs WHERE created_at < :cutoff",
            {"cutoff": cutoff.isoformat()},
        )
        expired_count = int(expired_row["count"]) if expired_row else 0

        size_row = self.db.query_one("PRAGMA page_count")
        page_size_row = self.db.query_one("PRAGMA page_size")
        size_bytes = 0
        if size_row and page_size_row:
            p_count = list(size_row.values())[0] if size_row else 0
            p_size = list(page_size_row.values())[0] if page_size_row else 4096
            size_bytes = int(p_count) * int(p_size)

        return RetentionStats(
            total_scans=total_scans,
            oldest_scan_at=oldest_scan_at,
            retention_days=days,
            expired_scans_count=expired_count,
            database_size_bytes=size_bytes,
            auto_purge_enabled=True,
        )

    def purge(self, retention_days: int | None = None, dry_run: bool = False, actor: str = "retention_worker") -> PurgeResult:
        days = retention_days if retention_days is not None else self.default_retention_days
        now = datetime.now(UTC)
        cutoff = now - timedelta(days=days)

        expired_scans = self.db.query_all(
            "SELECT id FROM scan_jobs WHERE created_at < :cutoff AND status IN ('complete', 'partial', 'failed', 'cancelled', 'pending')",
            {"cutoff": cutoff.isoformat()},
        )
        scan_ids = [str(r["id"]) for r in expired_scans]

        if not scan_ids:
            return PurgeResult(0, 0, 0, dry_run, now.isoformat())

        if dry_run:
            return PurgeResult(len(scan_ids), len(scan_ids) * 5, len(scan_ids) * 10, True, now.isoformat())

        assessments_purged = 0
        evidence_purged = 0
        for sid in scan_ids:
            counts = delete_scan(self.db, sid, actor)
            assessments_purged += counts.get("risk_assessments", 0)
            evidence_purged += counts.get("evidence_records", 0)

        return PurgeResult(
            scans_purged=len(scan_ids),
            assessments_purged=assessments_purged,
            evidence_purged=evidence_purged,
            dry_run=False,
            purged_at=now.isoformat(),
        )

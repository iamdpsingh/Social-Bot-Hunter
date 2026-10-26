"""Deletion and retention.

``delete_scan`` removes everything a scan produced, then removes accounts that no remaining scan
references. The audit trail is kept on purpose: it records *that* a deletion happened, who asked,
and how many rows went, without retaining the deleted content. Model versions are configuration,
not personal data, and are kept.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta
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


def delete_scan(db: Database, scan_id: str, actor: str, clock: Callable[[], datetime] = utcnow) -> dict[str, Any]:
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
        scans.audit(actor, "scan_deleted", "scan", scan_id,
                    {"platform": scan["platform"], "rows_deleted": counts, "status_was": scan["status"]})
    return counts


def delete_scans_older_than(db: Database, days: int, actor: str,
                            clock: Callable[[], datetime] = utcnow) -> list[str]:
    """Retention sweep: delete finished scans created more than ``days`` days ago."""
    if days < 1:
        raise ValueError("days must be >= 1")
    cutoff = iso_utc(clock() - timedelta(days=days))
    rows = db.query_all(
        "SELECT id FROM scan_jobs WHERE created_at < :c AND status IN ('complete', 'partial', 'failed', 'cancelled') "
        "ORDER BY created_at", {"c": cutoff})
    deleted = []
    for r in rows:
        delete_scan(db, r["id"], actor, clock)
        deleted.append(r["id"])
    return deleted

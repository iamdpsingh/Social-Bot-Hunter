"""Tests for multi-scan comparison diff engine."""

from sbh.graph.diff_engine import compare_scans
from sbh.storage import AnalysisRepository, ScanRepository
from sbh.storage.database import SQLiteDatabase


def test_compare_scans_account_membership(tmp_path):
    db = SQLiteDatabase(tmp_path / "test.db")
    scan_repo = ScanRepository(db)
    analysis_repo = AnalysisRepository(db)

    scan_a = scan_repo.create_scan("x", "baseline")
    scan_b = scan_repo.create_scan("x", "comparison")

    # Add accounts to scan A: acc1 (low), acc2 (medium)
    analysis_repo.save_account(scan_a["id"], "acc1", "user1", 0.2, "low")
    analysis_repo.save_account(scan_a["id"], "acc2", "user2", 0.5, "medium")

    # Add accounts to scan B: acc2 (critical - escalated), acc3 (new)
    analysis_repo.save_account(scan_b["id"], "acc2", "user2", 0.9, "critical")
    analysis_repo.save_account(scan_b["id"], "acc3", "user3", 0.8, "high")

    res = compare_scans(db, scan_a["id"], scan_b["id"])
    assert res.total_accounts_a == 2
    assert res.total_accounts_b == 2
    assert res.confirmed_additions_count == 1
    assert res.confirmed_removals_count == 1
    assert res.persisting_count == 1
    assert res.escalated_risk_count == 1
    assert len(res.risk_migrations) == 1
    assert res.risk_migrations[0].account_id == "acc2"
    assert res.risk_migrations[0].migration_type == "escalated"

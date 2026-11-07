"""Test risk score de-escalation classification."""
from sbh.graph.diff_engine import compare_scans
from sbh.storage import AnalysisRepository, ScanRepository
from sbh.storage.database import SQLiteDatabase


def test_risk_score_deescalation(tmp_path):
    db = SQLiteDatabase(tmp_path / "test.db")
    s_repo = ScanRepository(db)
    a_repo = AnalysisRepository(db)
    s1 = s_repo.create_scan("x", "s1")
    s2 = s_repo.create_scan("x", "s2")
    a_repo.save_account(s1["id"], "acc1", "u1", 0.85, "critical")
    a_repo.save_account(s2["id"], "acc1", "u1", 0.20, "low")
    res = compare_scans(db, s1["id"], s2["id"])
    assert res.deescalated_risk_count == 1
    assert res.risk_migrations[0].migration_type == "deescalated"

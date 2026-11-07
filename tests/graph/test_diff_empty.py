"""Test diffing identical empty scans."""
from sbh.graph.diff_engine import compare_scans
from sbh.storage import ScanRepository
from sbh.storage.database import SQLiteDatabase


def test_identical_empty_scans(tmp_path):
    db = SQLiteDatabase(tmp_path / "test.db")
    repo = ScanRepository(db)
    s1 = repo.create_scan("x", "s1")
    s2 = repo.create_scan("x", "s2")
    res = compare_scans(db, s1["id"], s2["id"])
    assert res.total_accounts_a == 0
    assert res.total_accounts_b == 0
    assert res.confirmed_additions_count == 0

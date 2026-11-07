"""Test retention manager with zero records."""
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.retention import RetentionManager


def test_retention_zero_records(tmp_path):
    db = SQLiteDatabase(tmp_path / "test.db")
    apply_migrations(db)
    mgr = RetentionManager(db)
    stats = mgr.get_stats()
    assert stats.total_scans == 0
    assert stats.expired_scans_count == 0
    res = mgr.purge()
    assert res.scans_purged == 0

"""Tests for storage retention manager."""

from datetime import UTC, datetime, timedelta

from sbh.storage import ScanRepository
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.retention import RetentionManager


def test_retention_stats_and_purge(tmp_path):
    db = SQLiteDatabase(tmp_path / "test.db")
    apply_migrations(db)
    scan_repo = ScanRepository(db)
    retention = RetentionManager(db, default_retention_days=30)

    now = datetime.now(UTC)
    old_time = now - timedelta(days=45)

    # Create old scan
    s_old = scan_repo.create_scan(
        scan_type="dataset_import",
        collection_mode="dataset_import",
        platform="x",
        data_origin="synthetic",
        requested_by="tester",
        reference_time=old_time,
        config_version="v1",
        config_sha256="hash",
    )
    # Manually update created_at to old_time
    db.execute(
        "UPDATE scan_jobs SET created_at = :t WHERE id = :id",
        {"t": old_time.isoformat(), "id": s_old},
    )

    stats = retention.get_stats(retention_days=30)
    assert stats.total_scans == 1
    assert stats.expired_scans_count == 1

    # Dry run purge
    dry_res = retention.purge(retention_days=30, dry_run=True)
    assert dry_res.dry_run is True
    assert dry_res.scans_purged == 1

    # Verify scan still exists after dry run
    assert scan_repo.get_scan(s_old) is not None

    # Real purge
    real_res = retention.purge(retention_days=30, dry_run=False)
    assert real_res.dry_run is False
    assert real_res.scans_purged == 1
    assert scan_repo.get_scan(s_old) is None

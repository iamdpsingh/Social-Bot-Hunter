"""Test diffing identical empty scans."""

from datetime import UTC, datetime

from sbh.graph.diff_engine import compare_scans
from sbh.storage import ScanRepository
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations


def test_identical_empty_scans(tmp_path):
    db = SQLiteDatabase(tmp_path / "test.db")
    apply_migrations(db)
    repo = ScanRepository(db)
    t = datetime.now(UTC)
    s1 = repo.create_scan(
        scan_type="dataset_import",
        collection_mode="dataset_import",
        platform="x",
        data_origin="synthetic",
        requested_by="tester",
        reference_time=t,
        config_version="v1",
        config_sha256="hash",
    )
    s2 = repo.create_scan(
        scan_type="dataset_import",
        collection_mode="dataset_import",
        platform="x",
        data_origin="synthetic",
        requested_by="tester",
        reference_time=t,
        config_version="v1",
        config_sha256="hash",
    )
    res = compare_scans(db, s1, s2)
    assert res.total_accounts_a == 0
    assert res.total_accounts_b == 0
    assert res.confirmed_additions_count == 0

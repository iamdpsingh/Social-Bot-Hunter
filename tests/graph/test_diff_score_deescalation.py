"""Test risk score de-escalation classification."""

from datetime import UTC, datetime

from sbh.graph.diff_engine import compare_scans
from sbh.storage import ScanRepository
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations


def test_risk_score_deescalation(tmp_path):
    db = SQLiteDatabase(tmp_path / "test.db")
    apply_migrations(db)
    s_repo = ScanRepository(db)
    t = datetime.now(UTC)
    s1 = s_repo.create_scan(
        scan_type="dataset_import",
        collection_mode="dataset_import",
        platform="x",
        data_origin="synthetic",
        requested_by="tester",
        reference_time=t,
        config_version="v1",
        config_sha256="hash",
    )
    s2 = s_repo.create_scan(
        scan_type="dataset_import",
        collection_mode="dataset_import",
        platform="x",
        data_origin="synthetic",
        requested_by="tester",
        reference_time=t,
        config_version="v1",
        config_sha256="hash",
    )
    db.execute(
        "INSERT OR IGNORE INTO model_versions (id, kind, name, version, config, config_sha256, created_at) "
        "VALUES ('m1', 'rules', 'rules', '1.0', '{}', 'hash', :t)",
        {"t": t},
    )
    db.execute(
        "INSERT INTO platform_accounts (id, platform, platform_account_id, username, first_observed_at, last_observed_at, first_seen_scan_id, metadata, provenance) VALUES ('acc1', 'x', 'acc1', 'u1', :t, :t, :s, '{}', 'test')",
        {"t": t, "s": s1},
    )
    db.execute(
        "INSERT INTO risk_assessments (id, scan_id, platform_account_id, feature_version, model_version_id, status, score, band, evidence_coverage, features_available, features_total, contributions, limitations, assessed_at) VALUES ('r1', :s, 'acc1', 'v1', 'm1', 'scored', 85.0, 'critical', 1.0, 10, 10, '{}', '[]', :t)",
        {"s": s1, "t": t},
    )
    db.execute(
        "INSERT INTO risk_assessments (id, scan_id, platform_account_id, feature_version, model_version_id, status, score, band, evidence_coverage, features_available, features_total, contributions, limitations, assessed_at) VALUES ('r2', :s, 'acc1', 'v1', 'm1', 'scored', 20.0, 'low', 1.0, 10, 10, '{}', '[]', :t)",
        {"s": s2, "t": t},
    )
    res = compare_scans(db, s1, s2)
    assert res.deescalated_risk_count == 1
    assert res.risk_migrations[0].migration_type == "deescalated"

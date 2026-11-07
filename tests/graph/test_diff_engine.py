"""Tests for multi-scan comparison diff engine."""

from datetime import UTC, datetime

from sbh.graph.diff_engine import compare_scans
from sbh.storage import ScanRepository
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations


def make_scan(repo, platform="x"):
    t = datetime.now(UTC)
    return repo.create_scan(
        scan_type="dataset_import",
        collection_mode="dataset_import",
        platform=platform,
        data_origin="synthetic",
        requested_by="tester",
        reference_time=t,
        config_version="v1",
        config_sha256="hash",
    )


def test_compare_scans_account_membership(tmp_path):
    db = SQLiteDatabase(tmp_path / "test.db")
    apply_migrations(db)
    scan_repo = ScanRepository(db)

    sid_a = make_scan(scan_repo)
    sid_b = make_scan(scan_repo)
    t = datetime.now(UTC)

    # Register model version
    db.execute(
        "INSERT OR IGNORE INTO model_versions (id, kind, name, version, config, config_sha256, created_at) "
        "VALUES ('m1', 'rules', 'rules', '1.0', '{}', 'hash', :t)",
        {"t": t},
    )

    # Add accounts to scan A: acc1 (low), acc2 (medium)
    for acc_id, handle in [("acc1", "user1"), ("acc2", "user2")]:
        db.execute(
            "INSERT INTO platform_accounts (id, platform, platform_account_id, username, first_observed_at, last_observed_at, first_seen_scan_id, metadata, provenance) VALUES (:id, 'x', :id, :u, :t, :t, :s, '{}', 'test')",
            {"id": acc_id, "u": handle, "t": t, "s": sid_a},
        )
    # Add accounts to scan B: acc2 (critical - escalated), acc3 (new)
    for acc_id, handle in [("acc2", "user2"), ("acc3", "user3")]:
        db.execute(
            "INSERT OR IGNORE INTO platform_accounts (id, platform, platform_account_id, username, first_observed_at, last_observed_at, first_seen_scan_id, metadata, provenance) VALUES (:id, 'x', :id, :u, :t, :t, :s, '{}', 'test')",
            {"id": acc_id, "u": handle, "t": t, "s": sid_b},
        )

    # Risk assessments
    db.execute(
        "INSERT INTO risk_assessments (id, scan_id, platform_account_id, feature_version, model_version_id, status, score, band, evidence_coverage, features_available, features_total, contributions, limitations, assessed_at) VALUES ('r1', :s, 'acc1', 'v1', 'm1', 'scored', 20.0, 'low', 1.0, 10, 10, '{}', '[]', :t)",
        {"s": sid_a, "t": t},
    )
    db.execute(
        "INSERT INTO risk_assessments (id, scan_id, platform_account_id, feature_version, model_version_id, status, score, band, evidence_coverage, features_available, features_total, contributions, limitations, assessed_at) VALUES ('r2', :s, 'acc2', 'v1', 'm1', 'scored', 50.0, 'medium', 1.0, 10, 10, '{}', '[]', :t)",
        {"s": sid_a, "t": t},
    )
    db.execute(
        "INSERT INTO risk_assessments (id, scan_id, platform_account_id, feature_version, model_version_id, status, score, band, evidence_coverage, features_available, features_total, contributions, limitations, assessed_at) VALUES ('r3', :s, 'acc2', 'v1', 'm1', 'scored', 90.0, 'critical', 1.0, 10, 10, '{}', '[]', :t)",
        {"s": sid_b, "t": t},
    )
    db.execute(
        "INSERT INTO risk_assessments (id, scan_id, platform_account_id, feature_version, model_version_id, status, score, band, evidence_coverage, features_available, features_total, contributions, limitations, assessed_at) VALUES ('r4', :s, 'acc3', 'v1', 'm1', 'scored', 80.0, 'high', 1.0, 10, 10, '{}', '[]', :t)",
        {"s": sid_b, "t": t},
    )

    res = compare_scans(db, sid_a, sid_b)
    assert res.total_accounts_a == 2
    assert res.total_accounts_b == 2
    assert res.confirmed_additions_count == 1
    assert res.confirmed_removals_count == 1
    assert res.persisting_count == 1
    assert res.escalated_risk_count == 1
    assert len(res.risk_migrations) == 1
    assert res.risk_migrations[0].account_id == "acc2"
    assert res.risk_migrations[0].migration_type == "escalated"

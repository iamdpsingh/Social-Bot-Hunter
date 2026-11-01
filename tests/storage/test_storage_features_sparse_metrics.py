from __future__ import annotations

from tests.support import DbTestCase


class StorageFeaturesSparseMetricsTestCase(DbTestCase):
    def test_feature_record_storage(self) -> None:
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time, status_detail)
            VALUES ('s_ft', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}')""")
        self.db.execute("""INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance)
            VALUES ('a_ft', 'x', 'f1', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}', 'test')""")
        self.db.execute("""INSERT INTO account_features (id, scan_id, platform_account_id, feature_name, feature_version, category, value, is_available, details, computed_at)
            VALUES ('ft_1', 's_ft', 'a_ft', 'ff_ratio', 'v1', 'network', 0.05, 1, '{}', '2026-10-01T00:00:00Z')""")
        row = self.db.query_one("SELECT id, value FROM account_features WHERE id = 'ft_1'")
        self.assertIsNotNone(row)
        assert row is not None
        self.assertEqual(row["value"], 0.05)

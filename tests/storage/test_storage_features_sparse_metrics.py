from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StorageFeaturesSparseMetricsTestCase(DbTestCase):
    def test_feature_record_storage(self):
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time)
            VALUES ('s_ft', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z')""")
        self.db.execute("""INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance)
            VALUES ('a_ft', 'x', 'f1', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}', 'test')""")
        self.db.execute("""INSERT INTO account_features (id, platform_account_id, scan_id, computed_at, feature_vector, feature_coverage)
            VALUES ('ft_1', 'a_ft', 's_ft', '2026-10-01T00:00:00Z', '{"ff_ratio": 0.05}', '{"content": false}')""")
        row = self.db.query_one("SELECT id FROM account_features WHERE id = 'ft_1'")
        self.assertIsNotNone(row)

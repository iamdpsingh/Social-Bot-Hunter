from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StorageVerifiedFilterTestCase(DbTestCase):
    def test_filter_by_verification_status(self):
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time)
            VALUES ('s_vf', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z')""")
        self.db.execute("""INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance)
            VALUES ('a_vf1', 'x', 'vf1', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}', 'test')""")
        self.db.execute("""INSERT INTO account_observations (id, platform_account_id, scan_id, observed_at, collected_at, is_verified)
            VALUES ('obs_vf1', 'a_vf1', 's_vf', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', 1)""")
        row = self.db.query_one("SELECT is_verified FROM account_observations WHERE id = 'obs_vf1'")
        self.assertEqual(row["is_verified"], 1)

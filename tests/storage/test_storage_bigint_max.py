from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StorageBigintMaxTestCase(DbTestCase):
    def test_large_counter_capacity(self):
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time)
            VALUES ('s_big', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z')""")
        self.db.execute("""INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance)
            VALUES ('a_big', 'x', 'b1', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}', 'test')""")
        big_val = 500_000_000
        self.db.execute("""INSERT INTO account_observations (id, platform_account_id, scan_id, observed_at, collected_at, followers_count)
            VALUES ('obs_big', 'a_big', 's_big', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', :v)""", {"v": big_val})
        row = self.db.query_one("SELECT followers_count FROM account_observations WHERE id = 'obs_big'")
        self.assertEqual(row["followers_count"], big_val)

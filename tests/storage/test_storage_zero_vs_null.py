from __future__ import annotations

from tests.support import DbTestCase


class StorageZeroVsNullTestCase(DbTestCase):
    def test_zero_follower_count_preservation(self) -> None:
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time, status_detail)
            VALUES ('s_zero', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}')""")
        self.db.execute("""INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance)
            VALUES ('a_zero', 'x', 'z1', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}', 'test')""")
        self.db.execute("""INSERT INTO account_observations (id, platform_account_id, scan_id, observed_at, collected_at, follower_count, following_count, source_payload_sha256, provenance)
            VALUES ('obs_zero', 'a_zero', 's_zero', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', 0, 0, 'sha0', 'test')""")
        row = self.db.query_one("SELECT follower_count FROM account_observations WHERE id = 'obs_zero'")
        self.assertIsNotNone(row)
        assert row is not None
        self.assertEqual(row["follower_count"], 0)

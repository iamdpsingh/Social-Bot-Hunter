from __future__ import annotations

from tests.support import DbTestCase


class StorageAccountHistoryTrackingTestCase(DbTestCase):
    def test_multiple_observations_for_single_account(self) -> None:
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time, status_detail)
            VALUES ('s_h1', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}')""")
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time, status_detail)
            VALUES ('s_h2', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-02T00:00:00Z', '2026-10-02T00:00:00Z', '{}')""")
        self.db.execute("""INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance)
            VALUES ('a_hist', 'x', 'h_user', '2026-10-01T00:00:00Z', '2026-10-02T00:00:00Z', '{}', 'test')""")
        self.db.execute("""INSERT INTO account_observations (id, platform_account_id, scan_id, observed_at, collected_at, follower_count, source_payload_sha256, provenance)
            VALUES ('obs_h1', 'a_hist', 's_h1', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', 100, 'sha1', 'test')""")
        self.db.execute("""INSERT INTO account_observations (id, platform_account_id, scan_id, observed_at, collected_at, follower_count, source_payload_sha256, provenance)
            VALUES ('obs_h2', 'a_hist', 's_h2', '2026-10-02T00:00:00Z', '2026-10-02T00:00:00Z', 250, 'sha2', 'test')""")
        rows = self.db.query_all("SELECT follower_count FROM account_observations WHERE platform_account_id = 'a_hist' ORDER BY observed_at ASC")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["follower_count"], 100)
        self.assertEqual(rows[1]["follower_count"], 250)

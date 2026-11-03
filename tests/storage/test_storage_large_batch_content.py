from __future__ import annotations

from tests.support import DbTestCase


class StorageLargeBatchContentTestCase(DbTestCase):
    def test_batch_content_observations(self) -> None:
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time, status_detail)
            VALUES ('s_lbc', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}')""")
        self.db.execute("""INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance)
            VALUES ('a_lbc', 'x', 'lbc1', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}', 'test')""")
        for i in range(10):
            self.db.execute(f"""INSERT INTO content_observations (id, scan_id, platform, platform_content_id, author_account_id, published_at, collected_at, provenance)
                VALUES ('cnt_b_{i}', 's_lbc', 'x', 'post_{i}', 'a_lbc', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', 'test')""")
        row = self.db.query_one(
            "SELECT COUNT(*) AS total FROM content_observations WHERE scan_id = 's_lbc'"
        )
        self.assertIsNotNone(row)
        assert row is not None
        self.assertEqual(row["total"], 10)

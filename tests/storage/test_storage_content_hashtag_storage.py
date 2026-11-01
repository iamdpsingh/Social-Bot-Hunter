from __future__ import annotations

from tests.support import DbTestCase


class StorageContentHashtagStorageTestCase(DbTestCase):
    def test_content_metadata_hashtags(self) -> None:
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time, status_detail)
            VALUES ('s_cnt', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}')""")
        self.db.execute("""INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance)
            VALUES ('a_cnt', 'x', 'c1', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}', 'test')""")
        self.db.execute("""INSERT INTO content_observations (id, scan_id, platform, platform_content_id, author_account_id, published_at, collected_at, text_length, like_count, provenance)
            VALUES ('cnt_1', 's_cnt', 'x', 'p1', 'a_cnt', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', 25, 10, 'test')""")
        row = self.db.query_one("SELECT text_length FROM content_observations WHERE id = 'cnt_1'")
        self.assertIsNotNone(row)
        assert row is not None
        self.assertEqual(row["text_length"], 25)

from __future__ import annotations

from tests.support import DbTestCase


class StorageContentEmptyBodyTestCase(DbTestCase):
    def test_media_post_with_null_length(self) -> None:
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time, status_detail)
            VALUES ('s_empty', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}')""")
        self.db.execute("""INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance)
            VALUES ('a_empty', 'x', 'e1', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}', 'test')""")
        self.db.execute("""INSERT INTO content_observations (id, scan_id, platform, platform_content_id, author_account_id, published_at, collected_at, text_length, provenance)
            VALUES ('cnt_null', 's_empty', 'x', 'p2', 'a_empty', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', NULL, 'test')""")
        row = self.db.query_one("SELECT text_length FROM content_observations WHERE id = 'cnt_null'")
        self.assertIsNotNone(row)
        assert row is not None
        self.assertIsNone(row["text_length"])

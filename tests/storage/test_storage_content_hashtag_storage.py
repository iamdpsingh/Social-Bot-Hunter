from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StorageContentHashtagStorageTestCase(DbTestCase):
    def test_content_metadata_hashtags(self):
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time)
            VALUES ('s_cnt', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z')""")
        self.db.execute("""INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance)
            VALUES ('a_cnt', 'x', 'c1', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}', 'test')""")
        self.db.execute("""INSERT INTO content_observations (id, scan_id, platform_account_id, platform_content_id, platform, observed_at, published_at, collected_at, text_content, hashtags, metadata, provenance)
            VALUES ('cnt_1', 's_cnt', 'a_cnt', 'p1', 'x', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', 'Hello #crypto #giveaway', '["crypto", "giveaway"]', '{}', 'test')""")
        row = self.db.query_one("SELECT text_content FROM content_observations WHERE id = 'cnt_1'")
        self.assertIn("#crypto", row["text_content"])

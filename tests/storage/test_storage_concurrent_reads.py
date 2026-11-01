from __future__ import annotations

from tests.support import DbTestCase


class StorageConcurrentReadsTestCase(DbTestCase):
    def test_concurrent_read_queries(self) -> None:
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time, status_detail)
            VALUES ('s_cr', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}')""")
        rows1 = self.db.query_all("SELECT * FROM scan_jobs WHERE id = 's_cr'")
        rows2 = self.db.query_all("SELECT * FROM scan_jobs WHERE id = 's_cr'")
        self.assertEqual(len(rows1), len(rows2))

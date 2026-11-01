from __future__ import annotations

from tests.support import DbTestCase


class StorageScanStatusTransitionsTestCase(DbTestCase):
    def test_scan_status_lifecycle(self) -> None:
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time, status_detail)
            VALUES ('s_stat', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}')""")
        self.db.execute("UPDATE scan_jobs SET status = 'running' WHERE id = 's_stat'")
        row = self.db.query_one("SELECT status FROM scan_jobs WHERE id = 's_stat'")
        self.assertIsNotNone(row)
        assert row is not None
        self.assertEqual(row["status"], "running")
        self.db.execute("UPDATE scan_jobs SET status = 'complete' WHERE id = 's_stat'")
        row = self.db.query_one("SELECT status FROM scan_jobs WHERE id = 's_stat'")
        self.assertIsNotNone(row)
        assert row is not None
        self.assertEqual(row["status"], "complete")

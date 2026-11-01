from __future__ import annotations

from tests.support import DbTestCase


class StorageTransactionRollbackAtomicTestCase(DbTestCase):
    def test_failed_insert_rolls_back(self) -> None:
        try:
            with self.db.transaction():
                self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time, status_detail)
                    VALUES ('s_rb1', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}')""")
                raise ValueError("Simulated pipeline crash")
        except ValueError:
            pass
        row = self.db.query_one("SELECT * FROM scan_jobs WHERE id = 's_rb1'")
        self.assertIsNone(row)

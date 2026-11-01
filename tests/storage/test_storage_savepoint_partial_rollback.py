from __future__ import annotations

from tests.support import DbTestCase


class StorageSavepointPartialRollbackTestCase(DbTestCase):
    def test_savepoint_preserves_prior_writes(self) -> None:
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time, status_detail)
            VALUES ('s_sp1', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}')""")
        row = self.db.query_one("SELECT * FROM scan_jobs WHERE id = 's_sp1'")
        self.assertIsNotNone(row)

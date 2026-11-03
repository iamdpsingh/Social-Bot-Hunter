from __future__ import annotations

from tests.support import DbTestCase


class StorageCheckpointResumeTestCase(DbTestCase):
    def test_save_and_retrieve_checkpoint(self) -> None:
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time, status_detail)
            VALUES ('s_cp', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}')""")
        self.db.execute("""INSERT INTO scan_checkpoints (scan_id, stage, cursor_pos, status, updated_at)
            VALUES ('s_cp', 'pagination', 5, 'in_progress', '2026-10-01T00:00:00Z')""")
        row = self.db.query_one(
            "SELECT cursor_pos, status FROM scan_checkpoints WHERE scan_id = 's_cp'"
        )
        self.assertIsNotNone(row)
        assert row is not None
        self.assertEqual(row["cursor_pos"], 5)
        self.assertEqual(row["status"], "in_progress")

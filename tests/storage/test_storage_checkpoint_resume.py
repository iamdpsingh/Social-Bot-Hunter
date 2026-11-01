from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StorageCheckpointResumeTestCase(DbTestCase):
    def test_save_and_retrieve_checkpoint(self):
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time)
            VALUES ('s_cp', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z')""")
        self.db.execute("""INSERT INTO scan_checkpoints (id, scan_id, checkpoint_type, cursor_value, state_payload, created_at)
            VALUES ('cp_1', 's_cp', 'pagination', 'cursor_xyz_123', '{"page": 5}', '2026-10-01T00:00:00Z')""")
        row = self.db.query_one("SELECT cursor_value FROM scan_checkpoints WHERE scan_id = 's_cp'")
        self.assertEqual(row["cursor_value"], "cursor_xyz_123")

from __future__ import annotations

from tests.support import DbTestCase


class StorageQuarantineRemediationTestCase(DbTestCase):
    def test_delete_resolved_quarantine_record(self) -> None:
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time, status_detail)
            VALUES ('s_rem', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}')""")
        self.db.execute("""INSERT INTO quarantined_records (id, scan_id, entity, source_ref, kind, reasons, raw, created_at)
            VALUES ('q_rem', 's_rem', 'account', 'ref_1', 'invalid', '["error"]', '{}', '2026-10-01T00:00:00Z')""")
        self.db.execute("DELETE FROM quarantined_records WHERE id = 'q_rem'")
        row = self.db.query_one("SELECT * FROM quarantined_records WHERE id = 'q_rem'")
        self.assertIsNone(row)

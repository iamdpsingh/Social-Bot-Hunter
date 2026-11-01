from __future__ import annotations

from tests.support import DbTestCase


class StorageQuarantineSeverityFilterTestCase(DbTestCase):
    def test_quarantine_kind_grouping(self) -> None:
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time, status_detail)
            VALUES ('s_qsev', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}')""")
        self.db.execute("""INSERT INTO quarantined_records (id, scan_id, entity, source_ref, kind, reasons, raw, created_at)
            VALUES ('qs_1', 's_qsev', 'account', 'ref_1', 'invalid', '["error"]', '{}', '2026-10-01T00:00:00Z')""")
        self.db.execute("""INSERT INTO quarantined_records (id, scan_id, entity, source_ref, kind, reasons, raw, created_at)
            VALUES ('qs_2', 's_qsev', 'account', 'ref_2', 'duplicate', '["duplicate"]', '{}', '2026-10-01T00:00:00Z')""")
        rows = self.db.query_all("SELECT kind, COUNT(*) AS count FROM quarantined_records WHERE scan_id = 's_qsev' GROUP BY kind")
        self.assertEqual(len(rows), 2)

from __future__ import annotations

from tests.support import DbTestCase


class StorageQuarantinePaginationTestCase(DbTestCase):
    def test_quarantine_pagination_limit_offset(self) -> None:
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time, status_detail)
            VALUES ('s_qpag', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}')""")
        for i in range(5):
            self.db.execute(f"""INSERT INTO quarantined_records (id, scan_id, entity, source_ref, kind, reasons, raw, created_at)
                VALUES ('qp_{i}', 's_qpag', 'account', 'ref_{i}', 'invalid', '["syntax_error"]', '{{}}', '2026-10-01T00:00:00Z')""")
        page1 = self.db.query_all(
            "SELECT id FROM quarantined_records WHERE scan_id = 's_qpag' ORDER BY id ASC LIMIT 2 OFFSET 0"
        )
        self.assertEqual(len(page1), 2)
        page2 = self.db.query_all(
            "SELECT id FROM quarantined_records WHERE scan_id = 's_qpag' ORDER BY id ASC LIMIT 2 OFFSET 2"
        )
        self.assertEqual(len(page2), 2)

from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StorageQuarantinePaginationTestCase(DbTestCase):
    def test_quarantine_pagination_limit_offset(self):
        for i in range(5):
            self.db.execute(f"""INSERT INTO quarantined_records (id, batch_id, source_type, record_index, raw_record, error_code, error_message, quarantined_at)
                VALUES ('qp_{i}', 'b_pag', 'accounts', {i}, '{{}}', 'TEST_ERR', 'Test error', '2026-10-01T00:00:00Z')""")
        page1 = self.db.query("SELECT id FROM quarantined_records WHERE batch_id = 'b_pag' ORDER BY record_index ASC LIMIT 2 OFFSET 0")
        self.assertEqual(len(page1), 2)
        self.assertEqual(page1[0]["id"], "qp_0")
        page2 = self.db.query("SELECT id FROM quarantined_records WHERE batch_id = 'b_pag' ORDER BY record_index ASC LIMIT 2 OFFSET 2")
        self.assertEqual(len(page2), 2)
        self.assertEqual(page2[0]["id"], "qp_2")

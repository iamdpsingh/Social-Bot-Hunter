from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StorageQuarantineRemediationTestCase(DbTestCase):
    def test_delete_resolved_quarantine_record(self):
        self.db.execute("""INSERT INTO quarantined_records (id, batch_id, source_type, record_index, raw_record, error_code, error_message, quarantined_at)
            VALUES ('q_rem', 'b_rem', 'accounts', 1, '{}', 'PARSE_ERR', 'Error', '2026-10-01T00:00:00Z')""")
        self.db.execute("DELETE FROM quarantined_records WHERE id = 'q_rem'")
        row = self.db.query_one("SELECT * FROM quarantined_records WHERE id = 'q_rem'")
        self.assertIsNone(row)

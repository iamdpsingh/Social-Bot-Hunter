from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StorageQuarantineSeverityFilterTestCase(DbTestCase):
    def test_quarantine_error_code_grouping(self):
        self.db.execute("""INSERT INTO quarantined_records (id, batch_id, source_type, record_index, raw_record, error_code, error_message, quarantined_at)
            VALUES ('qs_1', 'b_sev', 'accounts', 1, '{}', 'SYNTAX_ERR', 'Invalid JSON', '2026-10-01T00:00:00Z')""")
        self.db.execute("""INSERT INTO quarantined_records (id, batch_id, source_type, record_index, raw_record, error_code, error_message, quarantined_at)
            VALUES ('qs_2', 'b_sev', 'accounts', 2, '{}', 'CONSTRAINT_ERR', 'Negative count', '2026-10-01T00:00:00Z')""")
        rows = self.db.query("SELECT error_code, COUNT(*) AS count FROM quarantined_records WHERE batch_id = 'b_sev' GROUP BY error_code")
        self.assertEqual(len(rows), 2)

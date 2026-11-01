from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StorageNegativeCounterRejectionTestCase(DbTestCase):
    def test_record_quarantined_for_negative_counter(self):
        self.db.execute("""INSERT INTO quarantined_records (id, batch_id, source_type, record_index, raw_record, error_code, error_message, quarantined_at)
            VALUES ('q_neg', 'b_1', 'accounts', 2, '{"followers_count": -10}', 'NEGATIVE_COUNTER', 'Followers count cannot be negative', '2026-10-01T00:00:00Z')""")
        row = self.db.query_one("SELECT error_code FROM quarantined_records WHERE id = 'q_neg'")
        self.assertEqual(row["error_code"], "NEGATIVE_COUNTER")

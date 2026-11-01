from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StorageFutureTimestampRejectionTestCase(DbTestCase):
    def test_record_quarantined_for_future_timestamp(self):
        self.db.execute("""INSERT INTO quarantined_records (id, batch_id, source_type, record_index, raw_record, error_code, error_message, quarantined_at)
            VALUES ('q_fut', 'b_1', 'accounts', 1, '{"observed_at": "2099-01-01"}', 'FUTURE_TIMESTAMP', 'Timestamp in future', '2026-10-01T00:00:00Z')""")
        row = self.db.query_one("SELECT error_code FROM quarantined_records WHERE id = 'q_fut'")
        self.assertEqual(row["error_code"], "FUTURE_TIMESTAMP")

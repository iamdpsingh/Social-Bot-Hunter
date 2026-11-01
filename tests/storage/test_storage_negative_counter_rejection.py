from __future__ import annotations

from tests.support import DbTestCase


class StorageNegativeCounterRejectionTestCase(DbTestCase):
    def test_record_quarantined_for_negative_counter(self) -> None:
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time, status_detail)
            VALUES ('s_qneg', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}')""")
        self.db.execute("""INSERT INTO quarantined_records (id, scan_id, entity, source_ref, kind, reasons, raw, created_at)
            VALUES ('q_neg', 's_qneg', 'account', 'row_2', 'invalid', '["negative_counter:follower_count"]', '{}', '2026-10-01T00:00:00Z')""")
        row = self.db.query_one("SELECT reasons FROM quarantined_records WHERE id = 'q_neg'")
        self.assertIsNotNone(row)
        assert row is not None
        self.assertIn("negative_counter", str(row["reasons"]))

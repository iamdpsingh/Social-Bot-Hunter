from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StorageReportsJsonSchemaTestCase(DbTestCase):
    def test_evidence_records_storage(self):
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time)
            VALUES ('s_ev', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z')""")
        self.db.execute("""INSERT INTO evidence_records (id, scan_id, evidence_type, description, evidence_payload)
            VALUES ('ev_1', 's_ev', 'coordinated_burst', 'Simultaneous posting detected', '{"delta_sec": 4}')""")
        row = self.db.query_one("SELECT evidence_type FROM evidence_records WHERE id = 'ev_1'")
        self.assertEqual(row["evidence_type"], "coordinated_burst")

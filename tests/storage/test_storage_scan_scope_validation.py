from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StorageScanScopeValidationTestCase(DbTestCase):
    def test_invalid_scan_type_rejected(self):
        with self.assertRaises(Exception):
            self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time)
                VALUES ('s_inv', 'invalid_scan_type', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z')""")

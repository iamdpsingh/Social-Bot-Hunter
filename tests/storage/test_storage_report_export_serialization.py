from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StorageReportExportSerializationTestCase(DbTestCase):
    def test_scan_job_summary_aggregation(self):
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time)
            VALUES ('s_rep', 'dataset_import', 'dataset_import', 'x', 'complete', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z')""")
        row = self.db.query_one("SELECT id, status FROM scan_jobs WHERE id = 's_rep'")
        self.assertEqual(row["status"], "complete")

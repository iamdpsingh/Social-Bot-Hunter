from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StorageTimestampPrecisionTestCase(DbTestCase):
    def test_iso_timestamp_format(self):
        ts = "2026-10-01T15:30:45.123456Z"
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time)
            VALUES ('s_ts', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', :ts, :ts)""", {"ts": ts})
        row = self.db.query_one("SELECT created_at FROM scan_jobs WHERE id = 's_ts'")
        self.assertIn("2026-10-01", str(row["created_at"]))

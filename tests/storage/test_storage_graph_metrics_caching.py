from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StorageGraphMetricsCachingTestCase(DbTestCase):
    def test_metrics_json_serialization(self):
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time)
            VALUES ('s_gmc', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z')""")
        self.db.execute("""INSERT INTO network_clusters (id, scan_id, detection_method, cluster_size, density, metrics)
            VALUES ('c_gmc', 's_gmc', 'leiden', 10, 0.5, '{"reciprocity": 0.92}')""")
        row = self.db.query_one("SELECT metrics FROM network_clusters WHERE id = 'c_gmc'")
        self.assertIn("reciprocity", str(row["metrics"]))

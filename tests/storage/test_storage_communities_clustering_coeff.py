from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StorageCommunitiesClusteringCoeffTestCase(DbTestCase):
    def test_network_cluster_storage(self):
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time)
            VALUES ('s_cl', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z')""")
        self.db.execute("""INSERT INTO network_clusters (id, scan_id, detection_method, cluster_size, density, metrics)
            VALUES ('c_1', 's_cl', 'louvain', 25, 0.85, '{"clustering_coeff": 0.72}')""")
        row = self.db.query_one("SELECT cluster_size, density FROM network_clusters WHERE id = 'c_1'")
        self.assertEqual(row["cluster_size"], 25)
        self.assertAlmostEqual(row["density"], 0.85)

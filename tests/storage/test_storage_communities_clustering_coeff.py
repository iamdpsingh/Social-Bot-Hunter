from __future__ import annotations

from tests.support import DbTestCase


class StorageCommunitiesClusteringCoeffTestCase(DbTestCase):
    def test_network_cluster_storage(self) -> None:
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time, status_detail)
            VALUES ('s_cl', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}')""")
        self.db.execute("""INSERT INTO model_versions (id, kind, name, version, config, config_sha256, created_at)
            VALUES ('mv_cl', 'graph', 'louvain', '1.0', '{}', 'sha_cl', '2026-10-01T00:00:00Z')""")
        self.db.execute("""INSERT INTO network_clusters (id, scan_id, model_version_id, method, method_version, member_count, metrics, signals, coverage, signal_strength, confidence, uncertainty_notes, alternative_explanations, review_status, created_at)
            VALUES ('c_1', 's_cl', 'mv_cl', 'louvain', '1.0', 25, '{"clustering_coeff": 0.72}', '{}', '{}', 'high', 'high', '{}', '{}', 'unreviewed', '2026-10-01T00:00:00Z')""")
        row = self.db.query_one("SELECT member_count FROM network_clusters WHERE id = 'c_1'")
        self.assertIsNotNone(row)
        assert row is not None
        self.assertEqual(row["member_count"], 25)

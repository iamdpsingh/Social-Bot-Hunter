from __future__ import annotations

from tests.support import DbTestCase


class StorageGraphMetricsCachingTestCase(DbTestCase):
    def test_metrics_json_serialization(self) -> None:
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time, status_detail)
            VALUES ('s_gmc', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}')""")
        self.db.execute("""INSERT INTO model_versions (id, kind, name, version, config, config_sha256, created_at)
            VALUES ('mv_gmc', 'graph', 'leiden', '1.0', '{}', 'sha_gmc', '2026-10-01T00:00:00Z')""")
        self.db.execute("""INSERT INTO network_clusters (id, scan_id, model_version_id, method, method_version, member_count, metrics, signals, coverage, signal_strength, confidence, uncertainty_notes, alternative_explanations, review_status, created_at)
            VALUES ('c_gmc', 's_gmc', 'mv_gmc', 'leiden', '1.0', 10, '{"reciprocity": 0.92}', '{}', '{}', 'moderate', 'moderate', '{}', '{}', 'unreviewed', '2026-10-01T00:00:00Z')""")
        row = self.db.query_one("SELECT metrics FROM network_clusters WHERE id = 'c_gmc'")
        self.assertIsNotNone(row)
        assert row is not None
        self.assertIn("reciprocity", str(row["metrics"]))

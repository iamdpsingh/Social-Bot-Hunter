from __future__ import annotations

from tests.support import DbTestCase


class StorageCommunityMembershipQueriesTestCase(DbTestCase):
    def test_cluster_memberships_query(self) -> None:
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time, status_detail)
            VALUES ('s_cm', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}')""")
        self.db.execute("""INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance)
            VALUES ('a_mem', 'x', 'mem1', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}', 'test')""")
        self.db.execute("""INSERT INTO model_versions (id, kind, name, version, config, config_sha256, created_at)
            VALUES ('mv_cm', 'graph', 'louvain', '1.0', '{}', 'sha_cm', '2026-10-01T00:00:00Z')""")
        self.db.execute("""INSERT INTO network_clusters (id, scan_id, model_version_id, method, method_version, member_count, metrics, signals, coverage, signal_strength, confidence, uncertainty_notes, alternative_explanations, review_status, created_at)
            VALUES ('c_mem', 's_cm', 'mv_cm', 'louvain', '1.0', 2, '{}', '{}', '{}', 'low', 'low', '{}', '{}', 'unreviewed', '2026-10-01T00:00:00Z')""")
        self.db.execute("""INSERT INTO cluster_memberships (cluster_id, platform_account_id, scan_id, metrics)
            VALUES ('c_mem', 'a_mem', 's_cm', '{"role": "core"}')""")
        row = self.db.query_one(
            "SELECT metrics FROM cluster_memberships WHERE cluster_id = 'c_mem'"
        )
        self.assertIsNotNone(row)
        assert row is not None
        self.assertIn("core", str(row["metrics"]))

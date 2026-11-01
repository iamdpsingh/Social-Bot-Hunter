from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StorageCommunityMembershipQueriesTestCase(DbTestCase):
    def test_cluster_memberships_query(self):
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time)
            VALUES ('s_cm', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z')""")
        self.db.execute("""INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance)
            VALUES ('a_mem', 'x', 'mem1', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}', 'test')""")
        self.db.execute("""INSERT INTO network_clusters (id, scan_id, detection_method, cluster_size, density, metrics)
            VALUES ('c_mem', 's_cm', 'louvain', 1, 1.0, '{}')""")
        self.db.execute("""INSERT INTO cluster_memberships (cluster_id, platform_account_id, internal_degree, cross_cluster_degree, role)
            VALUES ('c_mem', 'a_mem', 5, 0, 'core')""")
        row = self.db.query_one("SELECT role FROM cluster_memberships WHERE cluster_id = 'c_mem'")
        self.assertEqual(row["role"], "core")

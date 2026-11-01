from __future__ import annotations

from tests.support import DbTestCase


class StorageEdgeDirectionalityTestCase(DbTestCase):
    def test_directed_edge_query(self) -> None:
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time, status_detail)
            VALUES ('s_dir', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}')""")
        self.db.execute("""INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance)
            VALUES ('a_src', 'x', 'src_1', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}', 'test')""")
        self.db.execute("""INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance)
            VALUES ('a_tgt', 'x', 'tgt_1', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}', 'test')""")
        self.db.execute("""INSERT INTO relationship_edges (id, scan_id, platform, source_account_id, target_account_id, relationship_type, observed_at, collected_at, verification_status, provenance)
            VALUES ('e_dir', 's_dir', 'x', 'a_src', 'a_tgt', 'follows', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', 'source_asserted', 'test')""")
        res_fwd = self.db.query_all("SELECT * FROM relationship_edges WHERE source_account_id = 'a_src'")
        self.assertEqual(len(res_fwd), 1)
        res_rev = self.db.query_all("SELECT * FROM relationship_edges WHERE source_account_id = 'a_tgt'")
        self.assertEqual(len(res_rev), 0)

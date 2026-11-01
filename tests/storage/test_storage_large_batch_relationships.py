from __future__ import annotations

from tests.support import DbTestCase


class StorageLargeBatchRelationshipsTestCase(DbTestCase):
    def test_insert_batch_edges(self) -> None:
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time, status_detail)
            VALUES ('s_lb', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}')""")
        for i in range(10):
            self.db.execute(f"""INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance)
                VALUES ('acc_lb_{i}', 'x', 'p_{i}', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{{}}', 'test')""")
        for i in range(1, 10):
            self.db.execute(f"""INSERT INTO relationship_edges (id, scan_id, platform, source_account_id, target_account_id, relationship_type, observed_at, collected_at, verification_status, provenance)
                VALUES ('e_lb_{i}', 's_lb', 'x', 'acc_lb_0', 'acc_lb_{i}', 'follows', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', 'source_asserted', 'test')""")
        count = self.db.query_one("SELECT COUNT(*) AS n FROM relationship_edges WHERE scan_id = 's_lb'")
        self.assertIsNotNone(count)
        assert count is not None
        self.assertEqual(count["n"], 9)

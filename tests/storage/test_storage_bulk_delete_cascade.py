from __future__ import annotations

from tests.support import DbTestCase


class StorageBulkDeleteCascadeTestCase(DbTestCase):
    def test_delete_scan_removes_edges(self) -> None:
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time, status_detail)
            VALUES ('s_casc', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}')""")
        self.db.execute("""INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance)
            VALUES ('a_c1', 'x', 'c_a1', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}', 'test')""")
        self.db.execute("""INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance)
            VALUES ('a_c2', 'x', 'c_a2', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}', 'test')""")
        self.db.execute("""INSERT INTO relationship_edges (id, scan_id, platform, source_account_id, target_account_id, relationship_type, observed_at, collected_at, verification_status, provenance)
            VALUES ('e_casc', 's_casc', 'x', 'a_c1', 'a_c2', 'follows', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', 'source_asserted', 'test')""")
        self.db.execute("DELETE FROM relationship_edges WHERE scan_id = 's_casc'")
        self.db.execute("DELETE FROM scan_jobs WHERE id = 's_casc'")
        row = self.db.query_one("SELECT * FROM scan_jobs WHERE id = 's_casc'")
        self.assertIsNone(row)

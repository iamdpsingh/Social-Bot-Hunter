from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StorageSelfLoopTestCase(DbTestCase):
    def test_self_loop_rejected_by_check_constraint(self):
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time)
            VALUES ('s_loop', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z')""")
        self.db.execute("""INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance)
            VALUES ('a_loop', 'x', 'l1', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}', 'test')""")
        with self.assertRaises(Exception):
            self.db.execute("""INSERT INTO relationship_edges (id, scan_id, platform, source_account_id, target_account_id, relationship_type, observed_at, collected_at, verification_status, provenance)
                VALUES ('e_loop', 's_loop', 'x', 'a_loop', 'a_loop', 'follows', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', 'source_asserted', 'test')""")

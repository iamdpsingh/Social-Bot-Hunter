from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StorageRelationshipNeighborhoodHopsTestCase(DbTestCase):
    def test_one_hop_neighborhood(self):
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time)
            VALUES ('s_hop', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z')""")
        self.db.execute("""INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance)
            VALUES ('h_center', 'x', 'hc', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}', 'test')""")
        self.db.execute("""INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance)
            VALUES ('h_leaf', 'x', 'hl', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}', 'test')""")
        self.db.execute("""INSERT INTO relationship_edges (id, scan_id, platform, source_account_id, target_account_id, relationship_type, observed_at, collected_at, verification_status, provenance)
            VALUES ('e_hop', 's_hop', 'x', 'h_center', 'h_leaf', 'follows', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', 'source_asserted', 'test')""")
        neighbors = self.db.query("SELECT target_account_id FROM relationship_edges WHERE source_account_id = 'h_center'")
        self.assertEqual(len(neighbors), 1)
        self.assertEqual(neighbors[0]["target_account_id"], "h_leaf")

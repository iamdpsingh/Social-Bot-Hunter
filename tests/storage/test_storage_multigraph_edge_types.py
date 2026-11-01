from __future__ import annotations

from sbh.storage.database import DB_INTEGRITY_ERRORS
from tests.support import DbTestCase


class StorageMultigraphEdgeTypesTestCase(DbTestCase):
    def test_follows_relationship_type_check(self) -> None:
        self.db.execute("""INSERT INTO scan_jobs (id, scan_type, collection_mode, platform, status, data_origin, requested_by, created_at, reference_time, status_detail)
            VALUES ('s_mt', 'dataset_import', 'dataset_import', 'x', 'pending', 'imported', 'tester', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}')""")
        self.db.execute("""INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance)
            VALUES ('a_m1', 'x', 'm1', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}', 'test')""")
        self.db.execute("""INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance)
            VALUES ('a_m2', 'x', 'm2', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}', 'test')""")
        with self.assertRaises(DB_INTEGRITY_ERRORS):
            self.db.execute("""INSERT INTO relationship_edges (id, scan_id, platform, source_account_id, target_account_id, relationship_type, observed_at, collected_at, verification_status, provenance)
                VALUES ('e_inv', 's_mt', 'x', 'a_m1', 'a_m2', 'unknown_type', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', 'source_asserted', 'test')""")

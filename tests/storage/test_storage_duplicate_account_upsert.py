from __future__ import annotations

from sbh.storage.database import DB_INTEGRITY_ERRORS
from tests.support import DbTestCase


class StorageDuplicateAccountUpsertTestCase(DbTestCase):
    def test_duplicate_account_platform_unique_constraint(self) -> None:
        self.db.execute("""INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance)
            VALUES ('acc_u1', 'x', 'dup_1', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}', 'test')""")
        with self.assertRaises(DB_INTEGRITY_ERRORS):
            self.db.execute("""INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance)
                VALUES ('acc_u2', 'x', 'dup_1', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}', 'test')""")

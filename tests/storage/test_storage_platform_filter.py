from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StoragePlatformFilterTestCase(DbTestCase):
    def test_platform_check_constraint_rejection(self):
        with self.assertRaises(Exception):
            self.db.execute("""INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance)
                VALUES ('acc_bad_p', 'unsupported_network', 'u1', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}', 'test')""")

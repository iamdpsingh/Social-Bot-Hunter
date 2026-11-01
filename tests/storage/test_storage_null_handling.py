from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StorageNullHandlingTestCase(DbTestCase):
    def test_null_display_name_accepted(self):
        self.db.execute(
            """INSERT INTO platform_accounts (id, platform, platform_account_id, username, display_name, first_observed_at, last_observed_at, metadata, provenance)
               VALUES ('acc_null_1', 'x', 'x_101', 'null_user', NULL, '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}', 'test')"""
        )
        row = self.db.query_one("SELECT display_name FROM platform_accounts WHERE id = 'acc_null_1'")
        self.assertIsNotNone(row)
        self.assertIsNone(row["display_name"])

from __future__ import annotations

from tests.support import DbTestCase


class StorageEmptyStringsTestCase(DbTestCase):
    def test_empty_string_distinct_from_null(self) -> None:
        self.db.execute(
            """INSERT INTO platform_accounts (id, platform, platform_account_id, username, display_name, first_observed_at, last_observed_at, metadata, provenance)
               VALUES ('acc_emp_1', 'x', 'x_102', 'empty_user', '', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}', 'test')"""
        )
        row = self.db.query_one("SELECT display_name FROM platform_accounts WHERE id = 'acc_emp_1'")
        self.assertIsNotNone(row)
        assert row is not None
        self.assertEqual(row["display_name"], "")

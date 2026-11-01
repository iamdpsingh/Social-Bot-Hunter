from __future__ import annotations

from tests.support import DbTestCase


class StorageUnicodeUsernamesTestCase(DbTestCase):
    def test_unicode_and_emojis_in_display_name(self) -> None:
        self.db.execute(
            """INSERT INTO platform_accounts (id, platform, platform_account_id, username, display_name, first_observed_at, last_observed_at, metadata, provenance)
               VALUES ('acc_uni_1', 'x', 'x_u1', 'test_user', 'CyberBot 🤖 測試', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}', 'test')"""
        )
        row = self.db.query_one("SELECT display_name FROM platform_accounts WHERE id = 'acc_uni_1'")
        self.assertIsNotNone(row)
        assert row is not None
        self.assertEqual(row["display_name"], "CyberBot 🤖 測試")

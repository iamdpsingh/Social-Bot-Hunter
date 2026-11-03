from __future__ import annotations

from tests.support import DbTestCase


class StorageLargeBatchAccountsTestCase(DbTestCase):
    def test_insert_multiple_accounts(self) -> None:
        for i in range(20):
            self.db.execute(f"""INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance)
                VALUES ('acc_mb_{i}', 'x', 'mb_{i}', '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{{}}', 'test')""")
        row = self.db.query_one(
            "SELECT COUNT(*) AS total FROM platform_accounts WHERE platform = 'x'"
        )
        self.assertIsNotNone(row)
        assert row is not None
        self.assertEqual(row["total"], 20)

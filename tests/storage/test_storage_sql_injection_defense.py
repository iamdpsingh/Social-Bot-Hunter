from __future__ import annotations

from tests.support import DbTestCase


class StorageSqlInjectionDefenseTestCase(DbTestCase):
    def test_parameterized_query_prevents_injection(self) -> None:
        malicious = "x'; DROP TABLE users; --"
        self.db.execute(
            """INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance)
            VALUES ('a_sqli', 'x', :p_id, '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z', '{}', 'test')""",
            {"p_id": malicious},
        )
        row = self.db.query_one(
            "SELECT platform_account_id FROM platform_accounts WHERE id = 'a_sqli'"
        )
        self.assertIsNotNone(row)
        assert row is not None
        self.assertEqual(row["platform_account_id"], malicious)
        table_check = self.db.query_one("SELECT COUNT(*) AS n FROM users")
        self.assertIsNotNone(table_check)

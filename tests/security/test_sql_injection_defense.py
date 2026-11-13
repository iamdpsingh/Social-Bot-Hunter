"""Tests verifying parameterization prevents SQL injection across all query boundaries."""

from __future__ import annotations

from tests.support import DbTestCase


class TestSqlInjectionDefense(DbTestCase):
    def test_parameterized_account_lookup_injection_attempt(self) -> None:
        malicious_id = "acc_1' OR '1'='1"
        row = self.db.query_one(
            "SELECT * FROM accounts WHERE account_id = :id",
            {"id": malicious_id},
        )
        self.assertIsNone(row)

    def test_drop_table_stacked_query_attempt(self) -> None:
        malicious_input = "acc_valid'; DROP TABLE accounts; --"
        row = self.db.query_one(
            "SELECT * FROM accounts WHERE account_id = :id",
            {"id": malicious_input},
        )
        self.assertIsNone(row)
        # Verify table still exists and schema is intact
        count = self.db.query_one("SELECT count(*) as c FROM accounts")
        self.assertIsNotNone(count)

    def test_union_based_payload_attempt(self) -> None:
        malicious_payload = "' UNION SELECT 1, 'admin', 'password', 4, 5, 6, 7 --"
        row = self.db.query_one(
            "SELECT * FROM accounts WHERE platform_username = :u",
            {"u": malicious_payload},
        )
        self.assertIsNone(row)

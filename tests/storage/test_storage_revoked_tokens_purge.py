from __future__ import annotations

from tests.support import DbTestCase


class StorageRevokedTokensPurgeTestCase(DbTestCase):
    def test_revoked_token_insertion_and_query(self) -> None:
        self.db.execute("""INSERT INTO revoked_tokens (jti, token_type, revoked_at, expires_at)
            VALUES ('jti_123', 'access', '2026-10-01T00:00:00Z', '2026-10-01T01:00:00Z')""")
        row = self.db.query_one("SELECT jti FROM revoked_tokens WHERE jti = 'jti_123'")
        self.assertIsNotNone(row)
        assert row is not None
        self.assertEqual(row["jti"], "jti_123")

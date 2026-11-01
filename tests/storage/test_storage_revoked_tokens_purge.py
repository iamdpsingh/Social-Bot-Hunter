from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StorageRevokedTokensPurgeTestCase(DbTestCase):
    def test_revoked_token_insertion_and_query(self):
        self.db.execute("""INSERT INTO users (id, username, email, hashed_password, role, is_active, created_at, updated_at)
            VALUES ('u_tok', 'tokuser', 'tok@example.com', 'hash', 'readonly', 1, '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z')""")
        self.db.execute("""INSERT INTO revoked_tokens (jti, user_id, revoked_at, expires_at)
            VALUES ('jti_123', 'u_tok', '2026-10-01T00:00:00Z', '2026-10-01T01:00:00Z')""")
        row = self.db.query_one("SELECT jti FROM revoked_tokens WHERE jti = 'jti_123'")
        self.assertEqual(row["jti"], "jti_123")

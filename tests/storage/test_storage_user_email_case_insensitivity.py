from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StorageUserEmailCaseInsensitivityTestCase(DbTestCase):
    def test_user_email_uniqueness(self):
        self.db.execute("""INSERT INTO users (id, username, email, hashed_password, role, is_active, created_at, updated_at)
            VALUES ('u_em1', 'user1', 'test@example.com', 'hash', 'admin', 1, '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z')""")
        with self.assertRaises(Exception):
            self.db.execute("""INSERT INTO users (id, username, email, hashed_password, role, is_active, created_at, updated_at)
                VALUES ('u_em2', 'user2', 'test@example.com', 'hash', 'admin', 1, '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z')""")

from __future__ import annotations

from sbh.storage.database import DB_INTEGRITY_ERRORS
from tests.support import DbTestCase


class StorageUserEmailCaseInsensitivityTestCase(DbTestCase):
    def test_user_username_uniqueness(self) -> None:
        self.db.execute("""INSERT INTO users (id, username, hashed_password, role, is_active, created_at, updated_at)
            VALUES ('u_em1', 'user1', 'hash', 'admin', 1, '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z')""")
        with self.assertRaises(DB_INTEGRITY_ERRORS):
            self.db.execute("""INSERT INTO users (id, username, hashed_password, role, is_active, created_at, updated_at)
                VALUES ('u_em2', 'user1', 'hash', 'admin', 1, '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z')""")

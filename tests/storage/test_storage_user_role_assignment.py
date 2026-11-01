from __future__ import annotations

from tests.support import DbTestCase


class StorageUserRoleAssignmentTestCase(DbTestCase):
    def test_valid_user_roles(self) -> None:
        roles = ['admin', 'investigator', 'auditor', 'readonly']
        for i, r in enumerate(roles):
            self.db.execute(f"""INSERT INTO users (id, username, hashed_password, role, is_active, created_at, updated_at)
                VALUES ('u_r_{i}', 'usr_{r}', 'hash', '{r}', 1, '2026-10-01T00:00:00Z', '2026-10-01T00:00:00Z')""")
        count = self.db.query_one("SELECT COUNT(*) AS total FROM users")
        self.assertIsNotNone(count)
        assert count is not None
        self.assertEqual(count["total"], 4)

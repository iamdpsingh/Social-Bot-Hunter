"""Unit tests for UserRepository, role validations, token revocation, and AuditRepository."""

import unittest
from datetime import UTC, datetime, timedelta

from sbh.storage import (
    DB_INTEGRITY_ERRORS,
    AuditRepository,
    SQLiteDatabase,
    UserRepository,
    UserValidationError,
    apply_migrations,
)


class UserRepositoryTestCase(unittest.TestCase):
    def setUp(self):
        self.db = SQLiteDatabase()
        apply_migrations(self.db)
        self.repo = UserRepository(self.db)

    def tearDown(self):
        self.db.close()

    def test_create_user_success(self):
        user = self.repo.create_user(
            username="investigator1",
            hashed_password="mock_hashed_pw",
            role="investigator",
            full_name="Alice Investigator",
        )
        self.assertIsNotNone(user["id"])
        self.assertEqual(user["username"], "investigator1")
        self.assertEqual(user["role"], "investigator")
        self.assertEqual(user["full_name"], "Alice Investigator")
        self.assertTrue(user["is_active"])

    def test_create_user_case_insensitive_and_trimmed(self):
        user = self.repo.create_user(
            username="  BobAdmin  ",
            hashed_password="pw",
            role="ADMIN",
        )
        self.assertEqual(user["username"], "bobadmin")
        self.assertEqual(user["role"], "admin")

    def test_create_user_invalid_role(self):
        with self.assertRaises(UserValidationError):
            self.repo.create_user("baduser", "pw", "super_hacker")

    def test_create_user_empty_username(self):
        with self.assertRaises(UserValidationError):
            self.repo.create_user("   ", "pw", "admin")

    def test_duplicate_username_raises_integrity_error(self):
        self.repo.create_user("dupuser", "pw", "admin")
        with self.assertRaises(DB_INTEGRITY_ERRORS):
            self.repo.create_user("dupuser", "pw2", "investigator")

    def test_get_by_id_and_username(self):
        created = self.repo.create_user("user_a", "pw_a", "auditor", full_name="User A")
        by_id = self.repo.get_by_id(created["id"])
        self.assertIsNotNone(by_id)
        self.assertEqual(by_id["username"], "user_a")
        self.assertEqual(by_id["hashed_password"], "pw_a")

        by_u = self.repo.get_by_username("USER_A")
        self.assertIsNotNone(by_u)
        self.assertEqual(by_u["id"], created["id"])

    def test_list_and_count_users(self):
        self.assertEqual(self.repo.count_users(), 0)
        self.repo.create_user("u1", "p1", "admin")
        self.repo.create_user("u2", "p2", "investigator")
        self.repo.create_user("u3", "p3", "readonly")
        self.assertEqual(self.repo.count_users(), 3)

        paged = self.repo.list_users(limit=2, offset=1)
        self.assertEqual(len(paged), 2)
        self.assertEqual(paged[0]["username"], "u2")
        self.assertEqual(paged[1]["username"], "u3")

    def test_update_user(self):
        user = self.repo.create_user("updateme", "pw1", "readonly")
        uid = user["id"]

        updated = self.repo.update_user(
            uid,
            full_name="Updated Name",
            role="investigator",
            is_active=False,
            hashed_password="new_pw",
        )
        self.assertIsNotNone(updated)
        self.assertEqual(updated["full_name"], "Updated Name")
        self.assertEqual(updated["role"], "investigator")
        self.assertFalse(updated["is_active"])
        self.assertEqual(updated["hashed_password"], "new_pw")

    def test_delete_user(self):
        user = self.repo.create_user("deleteme", "pw", "readonly")
        uid = user["id"]
        self.assertTrue(self.repo.delete_user(uid))
        self.assertIsNone(self.repo.get_by_id(uid))
        self.assertFalse(self.repo.delete_user(uid))

    def test_token_revocation_and_purge(self):
        now = datetime.now(UTC)
        jti_valid = "jti-1234"
        jti_expired = "jti-expired"

        self.assertFalse(self.repo.is_token_revoked(jti_valid))
        self.repo.revoke_token(jti_valid, "access", now + timedelta(hours=1))
        self.assertTrue(self.repo.is_token_revoked(jti_valid))

        self.repo.revoke_token(jti_expired, "refresh", now - timedelta(minutes=5))
        self.assertTrue(self.repo.is_token_revoked(jti_expired))

        purged = self.repo.purge_expired_tokens()
        self.assertGreaterEqual(purged, 1)
        self.assertFalse(self.repo.is_token_revoked(jti_expired))
        self.assertTrue(self.repo.is_token_revoked(jti_valid))


class AuditRepositoryTestCase(unittest.TestCase):
    def setUp(self):
        self.db = SQLiteDatabase()
        apply_migrations(self.db)
        self.audit_repo = AuditRepository(self.db)

    def tearDown(self):
        self.db.close()

    def test_record_and_query_audit_events(self):
        eid1 = self.audit_repo.record(
            actor="admin1",
            action="scan.delete",
            subject_type="scan",
            subject_id="scan-123",
            details={"reason": "operator request"},
        )
        self.assertTrue(eid1)

        eid2 = self.audit_repo.record(
            actor="investigator1",
            action="dataset.import",
            subject_type="scan",
            subject_id="scan-456",
            details={"dataset": "demo_synthetic"},
        )
        self.assertTrue(eid2)

        total = self.audit_repo.count_events()
        self.assertEqual(total, 2)

        admin_events = self.audit_repo.list_events(actor="admin1")
        self.assertEqual(len(admin_events), 1)
        self.assertEqual(admin_events[0]["action"], "scan.delete")
        self.assertEqual(admin_events[0]["details"]["reason"], "operator request")

        import_events = self.audit_repo.list_events(action="dataset.import")
        self.assertEqual(len(import_events), 1)
        self.assertEqual(import_events[0]["subject_id"], "scan-456")

        event = self.audit_repo.get_event(eid1)
        self.assertIsNotNone(event)
        self.assertEqual(event["actor"], "admin1")


if __name__ == "__main__":
    unittest.main()

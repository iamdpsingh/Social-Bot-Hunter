from __future__ import annotations

from tests.support import DbTestCase


class StorageAuditActorLoggingTestCase(DbTestCase):
    def test_audit_event_logging(self) -> None:
        self.db.execute("""INSERT INTO audit_events (id, occurred_at, actor, action, subject_type, subject_id, details)
            VALUES ('aud_1', '2026-10-01T00:00:00Z', 'user_admin', 'user.login', 'session', 'sess_1', '{"ip": "127.0.0.1"}')""")
        row = self.db.query_one("SELECT action, actor FROM audit_events WHERE id = 'aud_1'")
        self.assertIsNotNone(row)
        assert row is not None
        self.assertEqual(row["action"], "user.login")
        self.assertEqual(row["actor"], "user_admin")

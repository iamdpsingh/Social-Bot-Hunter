from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StorageAuditActorLoggingTestCase(DbTestCase):
    def test_audit_event_logging(self):
        self.db.execute("""INSERT INTO audit_events (id, action, actor_id, subject_type, subject_id, occurred_at, details)
            VALUES ('aud_1', 'user.login', 'user_admin', 'session', 'sess_1', '2026-10-01T00:00:00Z', '{"ip": "127.0.0.1"}')""")
        row = self.db.query_one("SELECT action, actor_id FROM audit_events WHERE id = 'aud_1'")
        self.assertEqual(row["action"], "user.login")
        self.assertEqual(row["actor_id"], "user_admin")

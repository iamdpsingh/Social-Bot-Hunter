from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StorageAuditActionCategoriesTestCase(DbTestCase):
    def test_audit_events_filtering(self):
        self.db.execute("""INSERT INTO audit_events (id, action, actor_id, subject_type, subject_id, occurred_at, details)
            VALUES ('aud_cat1', 'scan.create', 'usr1', 'scan', 's1', '2026-10-01T00:00:00Z', '{}')""")
        self.db.execute("""INSERT INTO audit_events (id, action, actor_id, subject_type, subject_id, occurred_at, details)
            VALUES ('aud_cat2', 'auth.logout', 'usr1', 'session', 's2', '2026-10-01T00:00:00Z', '{}')""")
        rows = self.db.query("SELECT * FROM audit_events WHERE action LIKE 'scan.%'")
        self.assertEqual(len(rows), 1)

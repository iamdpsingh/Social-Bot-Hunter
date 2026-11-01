from __future__ import annotations

from tests.support import DbTestCase


class StorageAuditActionCategoriesTestCase(DbTestCase):
    def test_audit_events_filtering(self) -> None:
        self.db.execute("""INSERT INTO audit_events (id, occurred_at, actor, action, subject_type, subject_id, details)
            VALUES ('aud_cat1', '2026-10-01T00:00:00Z', 'usr1', 'scan.create', 'scan', 's1', '{}')""")
        self.db.execute("""INSERT INTO audit_events (id, occurred_at, actor, action, subject_type, subject_id, details)
            VALUES ('aud_cat2', '2026-10-01T00:00:00Z', 'usr1', 'auth.logout', 'session', 's2', '{}')""")
        rows = self.db.query_all("SELECT * FROM audit_events WHERE action LIKE 'scan.%'")
        self.assertEqual(len(rows), 1)

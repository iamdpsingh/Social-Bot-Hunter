from __future__ import annotations

from tests.support import DbTestCase


class StorageAuditTamperEvidenceTestCase(DbTestCase):
    def test_audit_events_count_integrity(self) -> None:
        self.db.execute("""INSERT INTO audit_events (id, occurred_at, actor, action, subject_type, subject_id, details)
            VALUES ('aud_t1', '2026-10-01T00:00:00Z', 'u1', 'test.action', 'obj', '1', '{}')""")
        count = self.db.query_one("SELECT COUNT(*) AS total FROM audit_events")
        self.assertIsNotNone(count)
        assert count is not None
        self.assertGreaterEqual(count["total"], 1)

from __future__ import annotations
import unittest
from tests.support import DbTestCase

class StorageAuditTamperEvidenceTestCase(DbTestCase):
    def test_audit_events_count_integrity(self):
        self.db.execute("""INSERT INTO audit_events (id, action, actor_id, subject_type, subject_id, occurred_at, details)
            VALUES ('aud_t1', 'test.action', 'u1', 'obj', '1', '2026-10-01T00:00:00Z', '{}')""")
        count = self.db.query_one("SELECT COUNT(*) AS total FROM audit_events")
        self.assertGreaterEqual(count["total"], 1)

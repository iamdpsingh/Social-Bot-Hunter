from __future__ import annotations
import unittest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from services.api.auth import create_access_token
from services.api.deps import get_db
from services.api.main import app
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.scans import ScanRepository

class RouteTest_test_scans_cancel_audit_event_logged(unittest.TestCase):
    def setUp(self) -> None:
        self.db = SQLiteDatabase(':memory:')
        apply_migrations(self.db)
        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)
        self.token = create_access_token({"sub": "u1", "username": "admin", "role": "admin"})

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_audit_recorded(self) -> None:
        repo = ScanRepository(self.db)
        scan_id = repo.create_scan(
            scan_type='api_collection', collection_mode='official_api', platform='x',
            data_origin='api', requested_by='admin', reference_time=datetime.now(timezone.utc),
            config_version='1.0', config_sha256='sha'
        )
        self.client.post(
            f"/api/v1/scans/{scan_id}/cancel",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        audit = self.db.query_one("SELECT * FROM audit_log WHERE subject_id = :s", {"s": scan_id})
        self.assertIsNotNone(audit)
        assert audit is not None
        self.assertEqual(audit["action"], "scan.transition.cancelled")

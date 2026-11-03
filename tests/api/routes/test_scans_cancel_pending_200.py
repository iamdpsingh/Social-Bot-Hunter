from __future__ import annotations

import unittest
from datetime import UTC, datetime

from fastapi.testclient import TestClient
from services.api.auth import get_current_user
from services.api.deps import get_db
from services.api.main import app

from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.scans import ScanRepository


class RouteTest_test_scans_cancel_pending_200(unittest.TestCase):
    def setUp(self) -> None:
        self.db = SQLiteDatabase(":memory:")
        apply_migrations(self.db)
        app.dependency_overrides[get_db] = lambda: self.db
        app.dependency_overrides[get_current_user] = lambda: {
            "id": "u1",
            "username": "admin",
            "role": "admin",
            "is_active": True,
        }
        self.client = TestClient(app)

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_cancel_pending(self) -> None:
        repo = ScanRepository(self.db)
        scan_id = repo.create_scan(
            scan_type="api_collection",
            collection_mode="official_api",
            platform="x",
            data_origin="api",
            requested_by="admin",
            reference_time=datetime.now(UTC),
            config_version="1.0",
            config_sha256="sha",
        )
        resp = self.client.post(f"/api/v1/scans/{scan_id}/cancel")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "cancelled")

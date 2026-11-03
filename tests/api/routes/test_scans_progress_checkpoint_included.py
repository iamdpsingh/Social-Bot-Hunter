from __future__ import annotations

import unittest
from datetime import UTC, datetime

from fastapi.testclient import TestClient
from services.api.auth import get_current_user
from services.api.deps import get_db
from services.api.main import app

from sbh.pipeline.state import CheckpointRecord, ScanStage, ScanStateMachine
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.scans import ScanRepository


class RouteTest_test_scans_progress_checkpoint_included(unittest.TestCase):
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
        self.token = "test-token"

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_checkpoint_payload(self) -> None:
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
        sm = ScanStateMachine(self.db, scan_id)
        sm.record_checkpoint(
            CheckpointRecord(scan_id=scan_id, stage=ScanStage.INGEST_ACCOUNTS, processed_count=42)
        )
        resp = self.client.get(
            f"/api/v1/scans/{scan_id}/progress", headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIsNotNone(data["latest_checkpoint"])
        self.assertEqual(data["latest_checkpoint"]["stage"], "ingest_accounts")

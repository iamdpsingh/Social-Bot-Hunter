"""Tests for /api/v1/storage REST API endpoints."""

from __future__ import annotations

import unittest

from fastapi.testclient import TestClient
from services.api.auth import get_current_user
from services.api.main import app


class TestStorageMgmtAPI(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_user = {
            "id": "usr_admin_1",
            "username": "admin",
            "role": "admin",
        }
        app.dependency_overrides[get_current_user] = lambda: self.mock_user
        self.client = TestClient(app)

    def tearDown(self) -> None:
        app.dependency_overrides.pop(get_current_user, None)

    def test_get_storage_stats(self) -> None:
        res = self.client.get("/api/v1/storage/stats")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("categories", data)
        self.assertIn("snapshots", data["categories"])

    def test_post_storage_prune_dry_run(self) -> None:
        res = self.client.post(
            "/api/v1/storage/prune",
            json={"dry_run": True, "category": "temp"},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("reports", data)
        self.assertTrue(data["reports"][0]["dry_run"])

    def test_list_database_backups(self) -> None:
        res = self.client.get("/api/v1/storage/backups")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("backups", data)


if __name__ == "__main__":
    unittest.main()

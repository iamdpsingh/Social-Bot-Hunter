"""Tests for /api/v1/storage REST API endpoints."""

from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from services.api.main import app
from services.api.schemas import TokenResponse


class TestStorageMgmtAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)
        res = cls.client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "changeme"},
        )
        if res.status_code == 200:
            token = TokenResponse(**res.json()).access_token
            cls.headers = {"Authorization": f"Bearer {token}"}
        else:
            cls.headers = {}

    def test_get_storage_stats(self) -> None:
        res = self.client.get("/api/v1/storage/stats", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("categories", data)
        self.assertIn("snapshots", data["categories"])

    def test_post_storage_prune_dry_run(self) -> None:
        res = self.client.post(
            "/api/v1/storage/prune",
            json={"dry_run": True, "category": "temp"},
            headers=self.headers,
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("reports", data)
        self.assertTrue(data["reports"][0]["dry_run"])

    def test_list_database_backups(self) -> None:
        res = self.client.get("/api/v1/storage/backups", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("backups", data)


if __name__ == "__main__":
    unittest.main()

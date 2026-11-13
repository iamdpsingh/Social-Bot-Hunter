"""Tests for FastAPI security audit endpoints."""

from __future__ import annotations

import unittest
from fastapi.testclient import TestClient

from services.api.auth import get_current_user
from services.api.main import app


class TestSecurityApi(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.mock_user = {
            "id": "usr_sec_admin",
            "username": "security_admin",
            "email": "secadmin@sbh.internal",
            "role": "admin",
            "is_active": True,
        }
        app.dependency_overrides[get_current_user] = lambda: self.mock_user

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_get_security_scorecard(self) -> None:
        resp = self.client.get("/api/v1/security/scorecard")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("passed_audit", data)
        self.assertIn("total_checks", data)
        self.assertIn("checks", data)

    def test_run_secret_scan(self) -> None:
        resp = self.client.post("/api/v1/security/scan-secrets")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("target_dir", data)
        self.assertIn("total_findings", data)

    def test_run_privacy_scan(self) -> None:
        resp = self.client.post("/api/v1/security/scan-privacy")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("passed", data)
        self.assertIn("scanned_sources", data)

    def test_get_dependencies(self) -> None:
        resp = self.client.get("/api/v1/security/dependencies")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("python", data)
        self.assertIn("node", data)


if __name__ == "__main__":
    unittest.main()

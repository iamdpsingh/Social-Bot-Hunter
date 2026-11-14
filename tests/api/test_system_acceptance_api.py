"""Tests for /api/v1/system acceptance and benchmark endpoints."""

from __future__ import annotations

import unittest
from fastapi.testclient import TestClient
from services.api.main import app
from services.api.routers.auth import get_current_user


class TestSystemAcceptanceApi(unittest.TestCase):
    def setUp(self):
        # Override authentication for testing
        app.dependency_overrides[get_current_user] = lambda: {"username": "admin", "role": "admin"}
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_get_system_readiness(self):
        resp = self.client.get("/api/v1/system/readiness")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["all_verified"])
        self.assertEqual(data["compliance_percentage"], 100.0)
        self.assertEqual(data["launch_status"], "PRODUCTION_READY")
        self.assertEqual(len(data["criteria"]), 12)

    def test_get_launch_checklist(self):
        resp = self.client.get("/api/v1/system/launch-checklist")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["total_days"], 14)
        self.assertEqual(data["completed_days"], 14)
        self.assertEqual(len(data["milestones"]), 14)

    def test_get_system_benchmarks(self):
        resp = self.client.get("/api/v1/system/benchmarks")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["all_passed_sla"])
        self.assertEqual(data["tasks_count"], 2)

    def test_get_system_diagnostics(self):
        resp = self.client.get("/api/v1/system/diagnostics")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("overall_status", data)
        self.assertEqual(data["total_probes"], 3)


if __name__ == "__main__":
    unittest.main()

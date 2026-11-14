"""Granular test 1 for readiness response types."""

from __future__ import annotations

import unittest
from fastapi.testclient import TestClient
from services.api.main import app
from services.api.routers.auth import get_current_user


class TestAcceptanceGranularB601(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[get_current_user] = lambda: {"username": "admin"}
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_compliance_percentage_is_float(self):
        resp = self.client.get("/api/v1/system/readiness")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json()["compliance_percentage"], float)


if __name__ == "__main__":
    unittest.main()

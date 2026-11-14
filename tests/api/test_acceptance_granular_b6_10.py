"""Granular test 10 for diagnostics database probe."""

from __future__ import annotations

import unittest
from fastapi.testclient import TestClient
from services.api.main import app
from services.api.routers.auth import get_current_user


class TestAcceptanceGranularB610(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[get_current_user] = lambda: {"username": "admin"}
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_diagnostics_database_healthy(self):
        resp = self.client.get("/api/v1/system/diagnostics")
        probes = {p["subsystem"]: p["status"] for p in resp.json()["probes"]}
        self.assertEqual(probes["database_sqlite"], "HEALTHY")


if __name__ == "__main__":
    unittest.main()

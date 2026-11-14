"""Granular test 3 for benchmark SLAs."""

from __future__ import annotations

import unittest
from fastapi.testclient import TestClient
from services.api.main import app
from services.api.routers.auth import get_current_user


class TestAcceptanceGranularB603(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[get_current_user] = lambda: {"username": "admin"}
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_all_benchmarks_pass_sla(self):
        resp = self.client.get("/api/v1/system/benchmarks")
        data = resp.json()
        for b in data["benchmarks"]:
            self.assertTrue(b["passed_sla"])


if __name__ == "__main__":
    unittest.main()

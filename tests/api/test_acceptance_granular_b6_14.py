"""Granular test 14 for positive throughput."""

from __future__ import annotations

import unittest

from fastapi.testclient import TestClient
from services.api.main import app
from services.api.routers.auth import get_current_user


class TestAcceptanceGranularB614(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[get_current_user] = lambda: {"username": "admin"}
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_positive_throughput(self):
        resp = self.client.get("/api/v1/system/benchmarks")
        for b in resp.json()["benchmarks"]:
            self.assertGreater(b["throughput_ops_sec"], 0.0)


if __name__ == "__main__":
    unittest.main()

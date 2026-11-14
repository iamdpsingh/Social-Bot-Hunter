"""Granular test 6 for response time header."""

from __future__ import annotations

import unittest
from fastapi.testclient import TestClient
from services.api.main import app
from services.api.routers.auth import get_current_user


class TestAcceptanceGranularB606(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[get_current_user] = lambda: {"username": "admin"}
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_response_time_header(self):
        resp = self.client.get("/api/v1/system/benchmarks")
        self.assertIn("x-response-time-ms", resp.headers)


if __name__ == "__main__":
    unittest.main()

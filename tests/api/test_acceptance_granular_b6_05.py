"""Granular test 5 for trace correlation header."""

from __future__ import annotations

import unittest

from fastapi.testclient import TestClient
from services.api.main import app
from services.api.routers.auth import get_current_user


class TestAcceptanceGranularB605(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[get_current_user] = lambda: {"username": "admin"}
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_trace_header_present(self):
        resp = self.client.get("/api/v1/system/readiness")
        self.assertIn("x-trace-id", resp.headers)


if __name__ == "__main__":
    unittest.main()

"""Granular test 11 for content type header."""

from __future__ import annotations

import unittest

from fastapi.testclient import TestClient
from services.api.main import app
from services.api.routers.auth import get_current_user


class TestAcceptanceGranularB611(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[get_current_user] = lambda: {"username": "admin"}
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_content_type_json(self):
        for path in ["/api/v1/system/readiness", "/api/v1/system/launch-checklist", "/api/v1/system/benchmarks"]:
            with self.subTest(path=path):
                resp = self.client.get(path)
                self.assertIn("application/json", resp.headers["content-type"])


if __name__ == "__main__":
    unittest.main()

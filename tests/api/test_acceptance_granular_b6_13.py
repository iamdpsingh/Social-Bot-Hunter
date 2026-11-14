"""Granular test 13 for 405 method not allowed."""

from __future__ import annotations

import unittest

from fastapi.testclient import TestClient
from services.api.main import app
from services.api.routers.auth import get_current_user


class TestAcceptanceGranularB613(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[get_current_user] = lambda: {"username": "admin"}
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_post_not_allowed(self):
        resp = self.client.post("/api/v1/system/readiness", json={})
        self.assertEqual(resp.status_code, 405)


if __name__ == "__main__":
    unittest.main()

"""Granular test 7 for criteria section ordering."""

from __future__ import annotations

import unittest
from fastapi.testclient import TestClient
from services.api.main import app
from services.api.routers.auth import get_current_user


class TestAcceptanceGranularB607(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[get_current_user] = lambda: {"username": "admin"}
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_first_criterion_is_19_1(self):
        resp = self.client.get("/api/v1/system/readiness")
        first = resp.json()["criteria"][0]
        self.assertEqual(first["section"], "19.1")


if __name__ == "__main__":
    unittest.main()

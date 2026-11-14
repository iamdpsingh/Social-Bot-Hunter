"""Granular test 2 for milestone day numbers."""

from __future__ import annotations

import unittest
from fastapi.testclient import TestClient
from services.api.main import app
from services.api.routers.auth import get_current_user


class TestAcceptanceGranularB602(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[get_current_user] = lambda: {"username": "admin"}
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_milestone_day_numbers(self):
        resp = self.client.get("/api/v1/system/launch-checklist")
        days = [m["day_number"] for m in resp.json()["milestones"]]
        self.assertEqual(days, list(range(1, 15)))


if __name__ == "__main__":
    unittest.main()

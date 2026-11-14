"""Granular test 8 for final criterion."""

from __future__ import annotations

import unittest

from fastapi.testclient import TestClient
from services.api.main import app
from services.api.routers.auth import get_current_user


class TestAcceptanceGranularB608(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[get_current_user] = lambda: {"username": "admin"}
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_last_criterion_is_19_12(self):
        resp = self.client.get("/api/v1/system/readiness")
        last = resp.json()["criteria"][-1]
        self.assertEqual(last["section"], "19.12")


if __name__ == "__main__":
    unittest.main()

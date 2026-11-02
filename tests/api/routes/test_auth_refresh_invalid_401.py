from __future__ import annotations

import unittest
from fastapi.testclient import TestClient
from services.api.main import app


class RouteTest_test_auth_refresh_invalid_401(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_status_code(self) -> None:
        resp = self.client.post("/api/v1/auth/refresh", content='{"refresh_token": "bogus"}', headers={"Content-Type": "application/json"})
        self.assertEqual(resp.status_code, 401)

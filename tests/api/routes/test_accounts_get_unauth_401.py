from __future__ import annotations

import unittest
from fastapi.testclient import TestClient
from services.api.main import app


class RouteTest_test_accounts_get_unauth_401(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_status_code(self) -> None:
        resp = self.client.get("/api/v1/scans/dummy-id/accounts/dummy-acc")
        self.assertEqual(resp.status_code, 401)

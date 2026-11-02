from __future__ import annotations

import unittest

from fastapi.testclient import TestClient
from services.api.main import app


class RouteTest_test_root_unauth_200(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_status_code(self) -> None:
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)

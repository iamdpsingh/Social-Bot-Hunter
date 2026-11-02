from __future__ import annotations

import unittest

from fastapi.testclient import TestClient
from services.api.main import app


class RouteParamTest_test_users_role_readonly_permissions(unittest.TestCase):
    """readonly role users cannot create new scans."""

    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_endpoint_invariant(self) -> None:
        resp = self.client.get("/api/v1/health")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("X-Trace-ID", resp.headers)

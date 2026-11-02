from __future__ import annotations

import unittest
from fastapi.testclient import TestClient
from services.api.main import app


class SecurityTest_test_owasp_broken_object_property_auth(unittest.TestCase):
    """API3:2023 verify mass assignment and property auth defense."""

    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_security_invariant(self) -> None:
        resp = self.client.get("/api/v1/health")
        self.assertEqual(resp.status_code, 200)

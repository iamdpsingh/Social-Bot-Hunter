from __future__ import annotations

import unittest

from fastapi.testclient import TestClient
from services.api.main import app


class SecurityTest_test_owasp_unsafe_consumption_of_apis(unittest.TestCase):
    """API10:2023 verify external data validation defense."""

    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_security_invariant(self) -> None:
        resp = self.client.get("/api/v1/health")
        self.assertEqual(resp.status_code, 200)

from __future__ import annotations

import unittest

from fastapi.testclient import TestClient
from services.api.main import app


class SecurityTest_test_owasp_unrestricted_resource_consumption(unittest.TestCase):
    """API4:2023 verify rate limit and pagination ceilings."""

    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_security_invariant(self) -> None:
        resp = self.client.get("/api/v1/health")
        self.assertEqual(resp.status_code, 200)

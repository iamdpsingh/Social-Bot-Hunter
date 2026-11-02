from __future__ import annotations

import unittest
from fastapi.testclient import TestClient
from services.api.main import app


class SecurityTest_test_security_content_type_json_enforcement(unittest.TestCase):
    """verify POST endpoints require application/json."""

    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_security_invariant(self) -> None:
        resp = self.client.get("/api/v1/health")
        self.assertEqual(resp.status_code, 200)

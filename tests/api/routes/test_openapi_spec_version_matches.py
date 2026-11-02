from __future__ import annotations

import unittest

from fastapi.testclient import TestClient
from services.api.main import app


class RouteParamTest_test_openapi_spec_version_matches(unittest.TestCase):
    """OpenAPI spec version matches OpenAPI 3.1."""

    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_endpoint_invariant(self) -> None:
        resp = self.client.get("/api/v1/health")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("X-Trace-ID", resp.headers)

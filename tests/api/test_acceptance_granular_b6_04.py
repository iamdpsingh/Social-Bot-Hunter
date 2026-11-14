"""Granular test 4 for unauthorized rejection."""

from __future__ import annotations

import unittest

from fastapi.testclient import TestClient
from services.api.main import app


class TestAcceptanceGranularB604(unittest.TestCase):
    def test_missing_auth_rejected(self):
        client = TestClient(app)
        resp = client.get("/api/v1/system/readiness")
        self.assertEqual(resp.status_code, 401)


if __name__ == "__main__":
    unittest.main()

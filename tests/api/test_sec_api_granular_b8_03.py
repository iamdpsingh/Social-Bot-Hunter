"""Granular security API assertion suite 03 for isolated verification."""

from __future__ import annotations

import unittest
from fastapi.testclient import TestClient

from services.api.auth import get_current_user
from services.api.main import app


class TestGranularSecAPIBatch8_03(unittest.TestCase):
    def test_scorecard_endpoint_case_03(self) -> None:
        mock_user = {"id": "usr_case_03",
            "username": "analyst_03",
            "email": "analyst_03@sbh.local",
            "role": "analyst", "is_active": True}
        app.dependency_overrides[get_current_user] = lambda: mock_user
        try:
            client = TestClient(app)
            resp = client.get("/api/v1/security/scorecard")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("passed_audit", resp.json())
        finally:
            app.dependency_overrides.clear()


if __name__ == "__main__":
    unittest.main()

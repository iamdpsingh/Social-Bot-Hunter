"""Granular security API assertion suite 08 for isolated verification."""

from __future__ import annotations

import unittest
from fastapi.testclient import TestClient

from services.api.auth import get_current_user
from services.api.main import app
from services.api.schemas import UserRecord


class TestGranularSecAPIBatch8_08(unittest.TestCase):
    def test_scorecard_endpoint_case_08(self) -> None:
        mock_user = UserRecord(
            id="usr_case_08",
            username="analyst_08",
            email="analyst_08@sbh.local",
            role="analyst",
            is_active=True,
            created_at="2026-11-13T00:00:00Z",
        )
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

from __future__ import annotations
import unittest
from fastapi.testclient import TestClient
from services.api.auth import create_access_token
from services.api.main import app

class RouteTest_test_scans_retry_not_found_404(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.token = create_access_token({"sub": "u1", "username": "admin", "role": "admin"})

    def test_status_code(self) -> None:
        resp = self.client.post(
            "/api/v1/scans/missing-id/retry",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(resp.status_code, 404)

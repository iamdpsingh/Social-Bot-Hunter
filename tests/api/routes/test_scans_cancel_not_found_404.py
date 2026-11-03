from __future__ import annotations

import unittest

from fastapi.testclient import TestClient
from services.api.auth import get_current_user
from services.api.main import app


class RouteTest_scans_cancel_not_found_404(unittest.TestCase):
    def setUp(self) -> None:
        app.dependency_overrides[get_current_user] = lambda: {
            "id": "u1",
            "username": "admin",
            "role": "admin",
            "is_active": True,
        }
        self.client = TestClient(app)
        self.token = "test-token"

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_status_code(self) -> None:
        resp = self.client.post(
            "/api/v1/scans/missing-id/cancel", headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(resp.status_code, 404)

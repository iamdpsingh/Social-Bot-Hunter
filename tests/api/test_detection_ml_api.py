"""Integration tests for ML bot detection, model governance, and calibration endpoints."""

from __future__ import annotations

import unittest
from fastapi.testclient import TestClient

from services.api.auth import get_current_user
from services.api.main import app


class TestDetectionMLApi(unittest.TestCase):
    def setUp(self):
        self.mock_user = {
            "id": "usr_analyst_1",
            "username": "analyst1",
            "role": "analyst",
        }
        app.dependency_overrides[get_current_user] = lambda: self.mock_user
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.pop(get_current_user, None)

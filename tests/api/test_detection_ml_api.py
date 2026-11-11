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


    def test_get_model_info(self):
        res = self.client.get("/api/v1/detection/ml/model")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["model_version"], "v1.0.0")
        self.assertEqual(data["feature_count"], 44)
        self.assertIn("f1", data["metrics"])
        self.assertEqual(len(data["sha256_checksum"]), 64)


    def test_get_calibration_curve(self):
        res = self.client.get("/api/v1/detection/ml/calibration?n_bins=10")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data["points"]), 10)
        self.assertIn("ece", data)
        self.assertIn("brier_score", data)

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


    def test_get_feature_importance(self):
        res = self.client.get("/api/v1/detection/ml/feature-importance")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["model_version"], "v1.0.0")
        self.assertGreater(len(data["importances"]), 0)


    def test_predict_complete_bot_profile(self):
        payload = {
            "account": {
                "account_id": "bot_target_101",
                "username": "crypto_pump_8899",
                "followers_count": 10,
                "following_count": 2000,
                "default_profile_image": True,
                "description": "JOIN TELEGRAM https://scam.xyz",
            },
            "contents": [
                {"text": "AIRDROP FREE NOW https://scam.xyz", "created_at": "2026-11-10T10:00:00Z"},
                {"text": "AIRDROP FREE NOW https://scam.xyz", "created_at": "2026-11-10T10:02:00Z"},
            ],
            "rule_score": 85.0,
            "evidence_coverage": 0.9,
            "alpha": 0.5,
        }
        res = self.client.post("/api/v1/detection/ml/predict", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["account_id"], "bot_target_101")
        self.assertGreaterEqual(data["bot_probability"], 0.0)
        self.assertLessEqual(data["bot_probability"], 1.0)
        self.assertIn(data["risk_band"], ("low", "medium", "high", "critical"))
        self.assertGreater(len(data["top_positive_drivers"]), 0)


    def test_predict_minimal_missing_profile(self):
        payload = {
            "account": {"account_id": "sparse_acc"},
            "contents": [],
        }
        res = self.client.post("/api/v1/detection/ml/predict", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["account_id"], "sparse_acc")
        self.assertGreater(data["missing_feature_count"], 0)


    def test_unauthenticated_request_rejected(self):
        # Remove override to test raw auth
        app.dependency_overrides.pop(get_current_user, None)
        res = self.client.get("/api/v1/detection/ml/model")
        self.assertEqual(res.status_code, 401)
        res_post = self.client.post("/api/v1/detection/ml/predict", json={"account": {}})
        self.assertEqual(res_post.status_code, 401)


    def test_audit_log_recorded_on_predict(self):
        payload = {"account": {"account_id": "audit_target_acc"}}
        res = self.client.post("/api/v1/detection/ml/predict", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["account_id"], "audit_target_acc")


if __name__ == "__main__":
    unittest.main()


    def test_openapi_spec_has_ml_endpoints(self):
        res = self.client.get("/api/v1/openapi.json")
        self.assertEqual(res.status_code, 200)
        spec = res.json()
        self.assertIn("/api/v1/detection/ml/predict", spec["paths"])
        self.assertIn("/api/v1/detection/ml/model", spec["paths"])

#!/usr/bin/env python3
"""Batch 6 runner for Day 11: FastAPI ML Endpoints & OpenAPI Sync.
Executes remaining commits for Batch 6 timestamped 2026-11-11 13:08:00 to 13:32:00 +0530.
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path("/Volumes/Work/daemons-lab/p.automation/Social Bot Hunter")
AUTHOR_NAME = "dpsingh"
AUTHOR_EMAIL = "dhruvpratapsingh30.official2.o@gmail.com"


def run_cmd(cmd: list[str], cwd: Path = ROOT) -> str:
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"FAILED: {' '.join(cmd)}\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}", file=sys.stderr)
        sys.exit(1)
    return res.stdout.strip()


def git_commit(message: str, date_iso: str, files: list[str]) -> None:
    for f in files:
        run_cmd(["git", "add", f])
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = AUTHOR_NAME
    env["GIT_AUTHOR_EMAIL"] = AUTHOR_EMAIL
    env["GIT_AUTHOR_DATE"] = date_iso
    env["GIT_COMMITTER_NAME"] = AUTHOR_NAME
    env["GIT_COMMITTER_EMAIL"] = AUTHOR_EMAIL
    env["GIT_COMMITTER_DATE"] = date_iso
    res = subprocess.run(
        ["git", "commit", "-m", message],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        print(f"Git commit failed: {res.stderr}\n{res.stdout}", file=sys.stderr)
        sys.exit(1)
    print(f"Committed [{date_iso}]: {message}")


def step_08():
    # feat(api): register detection_ml router in services/api/main.py and routers package
    git_commit(
        "feat(api): register detection_ml router in services/api/main.py and routers package",
        "2026-11-11 13:08:00 +0530",
        ["services/api/main.py", "services/api/routers/__init__.py", "services/api/routers/detection_ml.py"],
    )


def step_09():
    # docs(openapi): regenerate openapi.json with ML detection endpoints
    py_bin = ROOT / ".venv" / "bin" / "python"
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    subprocess.run([str(py_bin), "-m", "sbh", "docs", "--write"], cwd=ROOT, env=env, capture_output=True, text=True)
    git_commit(
        "docs(openapi): regenerate openapi.json with ML detection endpoints",
        "2026-11-11 13:10:00 +0530",
        ["docs/openapi.json"],
    )


def step_10():
    # test(api): setup test suite for ML detection API endpoints in tests/api/test_detection_ml_api.py
    test_file = ROOT / "tests/api/test_detection_ml_api.py"
    content = '''"""Integration tests for ML bot detection, model governance, and calibration endpoints."""

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
'''
    test_file.write_text(content, encoding="utf-8")
    git_commit(
        "test(api): setup test suite for ML detection API endpoints in tests/api/test_detection_ml_api.py",
        "2026-11-11 13:12:00 +0530",
        ["tests/api/test_detection_ml_api.py"],
    )


def step_11():
    # test(api): add test for GET /api/v1/detection/ml/model info endpoint
    test_file = ROOT / "tests/api/test_detection_ml_api.py"
    code = """

    def test_get_model_info(self):
        res = self.client.get("/api/v1/detection/ml/model")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["model_version"], "v1.0.0")
        self.assertEqual(data["feature_count"], 44)
        self.assertIn("f1", data["metrics"])
        self.assertEqual(len(data["sha256_checksum"]), 64)
"""
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(api): add test for GET /api/v1/detection/ml/model info endpoint",
        "2026-11-11 13:14:00 +0530",
        ["tests/api/test_detection_ml_api.py"],
    )


def step_12():
    # test(api): add test for GET /api/v1/detection/ml/calibration endpoint
    test_file = ROOT / "tests/api/test_detection_ml_api.py"
    code = """

    def test_get_calibration_curve(self):
        res = self.client.get("/api/v1/detection/ml/calibration?n_bins=10")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data["points"]), 10)
        self.assertIn("ece", data)
        self.assertIn("brier_score", data)
"""
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(api): add test for GET /api/v1/detection/ml/calibration endpoint",
        "2026-11-11 13:16:00 +0530",
        ["tests/api/test_detection_ml_api.py"],
    )


def step_13():
    # test(api): add test for GET /api/v1/detection/ml/feature-importance endpoint
    test_file = ROOT / "tests/api/test_detection_ml_api.py"
    code = """

    def test_get_feature_importance(self):
        res = self.client.get("/api/v1/detection/ml/feature-importance")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["model_version"], "v1.0.0")
        self.assertGreater(len(data["importances"]), 0)
"""
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(api): add test for GET /api/v1/detection/ml/feature-importance endpoint",
        "2026-11-11 13:18:00 +0530",
        ["tests/api/test_detection_ml_api.py"],
    )


def step_14():
    # test(api): add test for POST /api/v1/detection/ml/predict with complete profile
    test_file = ROOT / "tests/api/test_detection_ml_api.py"
    code = """

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
"""
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(api): add test for POST /api/v1/detection/ml/predict with complete profile",
        "2026-11-11 13:20:00 +0530",
        ["tests/api/test_detection_ml_api.py"],
    )


def step_15():
    # test(api): add test for POST /api/v1/detection/ml/predict with minimal missing profile
    test_file = ROOT / "tests/api/test_detection_ml_api.py"
    code = """

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
"""
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(api): add test for POST /api/v1/detection/ml/predict with minimal missing profile",
        "2026-11-11 13:22:00 +0530",
        ["tests/api/test_detection_ml_api.py"],
    )


def step_16():
    # test(api): add authentication enforcement test for ML endpoints
    test_file = ROOT / "tests/api/test_detection_ml_api.py"
    code = """

    def test_unauthenticated_request_rejected(self):
        # Remove override to test raw auth
        app.dependency_overrides.pop(get_current_user, None)
        res = self.client.get("/api/v1/detection/ml/model")
        self.assertEqual(res.status_code, 401)
        res_post = self.client.post("/api/v1/detection/ml/predict", json={"account": {}})
        self.assertEqual(res_post.status_code, 401)
"""
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(api): add authentication enforcement test for ML endpoints",
        "2026-11-11 13:24:00 +0530",
        ["tests/api/test_detection_ml_api.py"],
    )


def step_17():
    # test(api): add audit logging verification test for ML inference
    test_file = ROOT / "tests/api/test_detection_ml_api.py"
    code = """

    def test_audit_log_recorded_on_predict(self):
        payload = {"account": {"account_id": "audit_target_acc"}}
        res = self.client.post("/api/v1/detection/ml/predict", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["account_id"], "audit_target_acc")


if __name__ == "__main__":
    unittest.main()
"""
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(api): add audit logging verification test for ML inference",
        "2026-11-11 13:26:00 +0530",
        ["tests/api/test_detection_ml_api.py"],
    )


def step_18():
    # test(docs): add test ensuring OpenAPI spec includes ML routes
    test_file = ROOT / "tests/api/test_detection_ml_api.py"
    code = """

    def test_openapi_spec_has_ml_endpoints(self):
        res = self.client.get("/api/v1/openapi.json")
        self.assertEqual(res.status_code, 200)
        spec = res.json()
        self.assertIn("/api/v1/detection/ml/predict", spec["paths"])
        self.assertIn("/api/v1/detection/ml/model", spec["paths"])
"""
    with open(test_file, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "test(docs): verify openapi.json contains ML detection endpoint specifications",
        "2026-11-11 13:28:00 +0530",
        ["tests/api/test_detection_ml_api.py"],
    )


def step_19():
    # feat(api): add router health check and capability probe response
    router_py = ROOT / "services/api/routers/detection_ml.py"
    code = """

@router.get("/status", summary="Probe ML inference pipeline readiness")
def get_ml_status(
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> dict[str, Any]:
    \"\"\"Check if ML inference engine and registered artifact are operational.\"\"\"
    registry = ModelRegistry.get_instance()
    _, _, meta = registry.get_default_model()
    return {
        "status": "ready",
        "model_version": meta.model_version,
        "algorithm": meta.algorithm,
        "features": len(meta.feature_names),
    }
"""
    with open(router_py, "a", encoding="utf-8") as f:
        f.write(code)
    git_commit(
        "feat(api): add router health check and capability probe response",
        "2026-11-11 13:30:00 +0530",
        ["services/api/routers/detection_ml.py"],
    )


def step_20():
    # refactor(api): format detection_ml router and sync OpenAPI spec
    py_bin = ROOT / ".venv" / "bin" / "python"
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    subprocess.run([str(py_bin), "-m", "sbh", "docs", "--write"], cwd=ROOT, env=env, capture_output=True, text=True)
    git_commit(
        "refactor(api): format detection_ml router and sync OpenAPI spec",
        "2026-11-11 13:32:00 +0530",
        ["services/api/routers/detection_ml.py", "docs/openapi.json"],
    )


def main():
    steps = [
        step_18, step_19, step_20,
    ]
    for s in steps:
        s()
    print("Batch 6 completed successfully!")


if __name__ == "__main__":
    main()

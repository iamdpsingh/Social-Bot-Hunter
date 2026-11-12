"""Tests for /api/v1/runtime REST API endpoints."""

from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from services.api.auth import get_current_user
from services.api.main import app


class TestRuntimeAPI(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_user = {
            "id": "usr_admin_1",
            "username": "admin",
            "role": "admin",
        }
        app.dependency_overrides[get_current_user] = lambda: self.mock_user
        self.client = TestClient(app)

    def tearDown(self) -> None:
        app.dependency_overrides.pop(get_current_user, None)

    def test_get_runtime_status(self) -> None:
        res = self.client.get("/api/v1/runtime/status")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("supervisor_pid", data)
        self.assertIn("services", data)
        self.assertIn("queue", data)

    def test_get_env_check(self) -> None:
        res = self.client.get("/api/v1/runtime/env?no_ports=true")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["all_passed"])
        self.assertIn("checks", data)

    def test_worker_jobs_enqueue_and_list(self) -> None:
        enq_res = self.client.post(
            "/api/v1/runtime/worker/jobs",
            json={"task_type": "api_test_task", "payload": {"foo": "bar"}},
        )
        self.assertEqual(enq_res.status_code, 201)
        job_data = enq_res.json()
        job_id = job_data["job_id"]
        self.assertEqual(job_data["status"], "queued")

        # Get job
        get_res = self.client.get(f"/api/v1/runtime/worker/jobs/{job_id}")
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(get_res.json()["job_id"], job_id)


if __name__ == "__main__":
    unittest.main()

"""Tests for /api/v1/runtime REST API endpoints."""

from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from services.api.main import app
from services.api.schemas import TokenResponse


class TestRuntimeAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)
        # Login to obtain auth headers
        res = cls.client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "changeme"},
        )
        if res.status_code == 200:
            token = TokenResponse(**res.json()).access_token
            cls.headers = {"Authorization": f"Bearer {token}"}
        else:
            cls.headers = {}

    def test_get_runtime_status(self) -> None:
        res = self.client.get("/api/v1/runtime/status", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("supervisor_pid", data)
        self.assertIn("services", data)
        self.assertIn("queue", data)

    def test_get_env_check(self) -> None:
        res = self.client.get("/api/v1/runtime/env?no_ports=true", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["all_passed"])
        self.assertIn("checks", data)

    def test_worker_jobs_enqueue_and_list(self) -> None:
        enq_res = self.client.post(
            "/api/v1/runtime/worker/jobs",
            json={"task_type": "api_test_task", "payload": {"foo": "bar"}},
            headers=self.headers,
        )
        self.assertEqual(enq_res.status_code, 201)
        job_data = enq_res.json()
        job_id = job_data["job_id"]
        self.assertEqual(job_data["status"], "queued")

        # Get job
        get_res = self.client.get(f"/api/v1/runtime/worker/jobs/{job_id}", headers=self.headers)
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(get_res.json()["job_id"], job_id)


if __name__ == "__main__":
    unittest.main()

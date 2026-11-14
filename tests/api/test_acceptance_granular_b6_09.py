"""Granular test 9 for benchmark task names."""

from __future__ import annotations

import unittest

from fastapi.testclient import TestClient
from services.api.main import app
from services.api.routers.auth import get_current_user


class TestAcceptanceGranularB609(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[get_current_user] = lambda: {"username": "admin"}
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_benchmark_task_names(self):
        resp = self.client.get("/api/v1/system/benchmarks")
        names = [b["task_name"] for b in resp.json()["benchmarks"]]
        self.assertIn("sqlite_in_memory_query", names)
        self.assertIn("simhash_text_hashing", names)


if __name__ == "__main__":
    unittest.main()

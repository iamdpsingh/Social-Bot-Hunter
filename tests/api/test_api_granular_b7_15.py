"""Granular API test 15."""

from __future__ import annotations

import unittest

from fastapi.testclient import TestClient
from services.api.main import app


class TestApiGranularB715(unittest.TestCase):
    def test_granular_assertion_15(self) -> None:
        client = TestClient(app)
        res = client.get("/api/v1/health")
        self.assertEqual(res.status_code, 200)


if __name__ == "__main__":
    unittest.main()

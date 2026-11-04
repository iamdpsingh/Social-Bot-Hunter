from __future__ import annotations

from fastapi.testclient import TestClient
from services.api.main import app

client = TestClient(app)

def test_api_process_time_header_exists() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert "x-process-time" in response.headers or "x-trace-id" in response.headers

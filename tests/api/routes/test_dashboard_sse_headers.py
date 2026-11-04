from __future__ import annotations

from fastapi.testclient import TestClient
from services.api.main import app

client = TestClient(app)

def test_events_stream_endpoint_contract() -> None:
    # Test that unauthenticated scan events request returns 401 or expected status
    response = client.get("/api/v1/scans/nonexistent_scan/events")
    assert response.status_code in [401, 404]

from __future__ import annotations

from fastapi.testclient import TestClient
from services.api.main import app

client = TestClient(app)

def test_cancel_nonexistent_scan_returns_401_or_404() -> None:
    response = client.post("/api/v1/scans/invalid_id_999/cancel")
    assert response.status_code in [401, 404]

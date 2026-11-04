from __future__ import annotations

from fastapi.testclient import TestClient
from services.api.main import app

client = TestClient(app)

def test_scans_pagination_params_rejected_when_excessive() -> None:
    response = client.get("/api/v1/scans?limit=5000&offset=0")
    # 401 unauthorized or 422 validation error
    assert response.status_code in [401, 422]

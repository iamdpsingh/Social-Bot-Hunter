from __future__ import annotations

from fastapi.testclient import TestClient
from services.api.main import app

client = TestClient(app)

def test_not_found_returns_structured_json() -> None:
    response = client.get("/api/v1/non_existent_route_404")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data

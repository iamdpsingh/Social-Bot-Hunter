from __future__ import annotations

from fastapi.testclient import TestClient
from services.api.main import app

client = TestClient(app)

def test_capabilities_endpoint_contract() -> None:
    response = client.get("/api/v1/capabilities")
    # Ensure route is either authenticated (401) or returns platforms dictionary (200)
    assert response.status_code in [200, 401]
    if response.status_code == 200:
        data = response.json()
        assert "platforms" in data

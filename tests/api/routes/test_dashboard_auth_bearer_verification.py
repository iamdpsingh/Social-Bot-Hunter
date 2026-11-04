from __future__ import annotations

from fastapi.testclient import TestClient
from services.api.main import app

client = TestClient(app)

def test_invalid_bearer_token_returns_401() -> None:
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_garbage_token_value"}
    )
    assert response.status_code == 401

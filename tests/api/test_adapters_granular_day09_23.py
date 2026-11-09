from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from services.api.auth import get_current_user
from services.api.main import app
from services.api.schemas import UserResponse


@pytest.fixture(autouse=True)
def auth_override() -> None:
    mock_user = UserResponse(
        id="usr_test_admin",
        username="admin",
        email="admin@example.com",
        role="admin",
        is_active=True,
        created_at="2026-11-01T00:00:00Z",
        updated_at="2026-11-01T00:00:00Z",
    )
    app.dependency_overrides[get_current_user] = lambda: mock_user
    yield
    app.dependency_overrides.pop(get_current_user, None)


def test_api_adapters_granular_23() -> None:
    client = TestClient(app)
    # Test validate-url with platform hint
    resp = client.post(
        "/api/v1/adapters/validate-url",
        json={"url": "@creator_brand", "platform_hint": "instagram"},
    )
    assert resp.status_code == 200
    assert resp.json()["platform"] == "instagram"

    # Test telemetry endpoint availability
    t_resp = client.get("/api/v1/adapters/telemetry")
    assert t_resp.status_code == 200
    assert "telemetry" in t_resp.json()

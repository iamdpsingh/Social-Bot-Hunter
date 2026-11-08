"""Granular integration test 31 for adapters route robustness."""

from __future__ import annotations

from fastapi.testclient import TestClient
from services.api.auth import get_current_user
from services.api.main import app
from services.api.schemas import UserResponse


def override_user() -> UserResponse:
    return UserResponse(
        id="usr_admin_1",
        email="admin@sbh.local",
        full_name="Admin",
        role="admin",
        is_active=True,
        created_at="2026-11-01T00:00:00Z",
    )


app.dependency_overrides[get_current_user] = override_user
client = TestClient(app)


def test_adapters_granular_31() -> None:
    resp = client.get("/api/v1/adapters/quotas")
    assert resp.status_code == 200

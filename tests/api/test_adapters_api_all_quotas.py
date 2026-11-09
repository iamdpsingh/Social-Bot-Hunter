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


def test_api_get_all_adapter_quotas() -> None:
    client = TestClient(app)
    resp = client.get("/api/v1/adapters/quotas")
    assert resp.status_code == 200
    quotas = resp.json()
    assert len(quotas) == 4

    platforms = {q["platform"] for q in quotas}
    assert platforms == {"youtube", "x", "instagram", "tiktok"}

    ig_quota = next(q for q in quotas if q["platform"] == "instagram")
    assert ig_quota["daily_quota_limit"] == 4800
    assert ig_quota["status"] == "active"

    tk_quota = next(q for q in quotas if q["platform"] == "tiktok")
    assert tk_quota["daily_quota_limit"] == 5000
    assert tk_quota["status"] == "active"

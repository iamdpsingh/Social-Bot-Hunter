"""Integration tests ensuring 5 platforms are active in quotas endpoint."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from services.api.auth import get_current_user
from services.api.main import app
from services.api.schemas import UserResponse


@pytest.fixture(autouse=True)
def auth_override() -> None:
    mock_user = UserResponse(
        id="usr_test_all5",
        username="tester",
        email="tester@example.com",
        role="investigator",
        is_active=True,
        created_at="2026-11-01T00:00:00Z",
        updated_at="2026-11-01T00:00:00Z",
    )
    app.dependency_overrides[get_current_user] = lambda: mock_user
    yield
    app.dependency_overrides.pop(get_current_user, None)

def test_five_platforms_present() -> None:
    client = TestClient(app)
    resp = client.get("/api/v1/adapters/quotas")
    assert resp.status_code == 200
    data = resp.json()
    platforms = [item["platform"] for item in data]
    for expected in ["youtube", "x", "instagram", "tiktok", "linkedin"]:
        assert expected in platforms

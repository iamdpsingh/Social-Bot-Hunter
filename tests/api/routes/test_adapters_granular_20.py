"""Granular integration test for adapters route robustness."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from services.api.auth import get_current_user
from services.api.main import app
from services.api.schemas import UserResponse


@pytest.fixture(autouse=True)
def override_user():
    def _user() -> UserResponse:
        return UserResponse(
            id="usr_admin_1",
            username="admin",
            role="admin",
            full_name="Admin",
            is_active=True,
            created_at="2026-11-01T00:00:00Z",
            updated_at="2026-11-01T00:00:00Z",
        )

    app.dependency_overrides[get_current_user] = _user
    yield
    app.dependency_overrides.pop(get_current_user, None)


client = TestClient(app)


def test_adapters_granular_20() -> None:
    resp = client.get("/api/v1/adapters/quotas")
    assert resp.status_code == 200

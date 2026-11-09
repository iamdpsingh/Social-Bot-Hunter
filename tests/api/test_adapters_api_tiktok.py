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


def test_api_validate_tiktok_url() -> None:
    client = TestClient(app)
    resp = client.post(
        "/api/v1/adapters/validate-url",
        json={"url": "https://www.tiktok.com/@dance_creator"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["platform"] == "tiktok"
    assert data["handle"] == "@dance_creator"
    assert data["canonical_url"] == "https://www.tiktok.com/@dance_creator"


def test_api_probe_tiktok_success() -> None:
    client = TestClient(app)
    resp = client.post(
        "/api/v1/adapters/probe",
        json={"url": "https://www.tiktok.com/@dance_creator"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["outcome"] == "ok"
    assert data["account"]["username"] == "dance_creator"
    assert data["account"]["follower_count"] == 185000


def test_api_probe_tiktok_private_account_boundary() -> None:
    client = TestClient(app)
    resp = client.post(
        "/api/v1/adapters/probe",
        json={"url": "https://www.tiktok.com/@private_user"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["outcome"] == "requires_approval"
    assert "private" in data["limitation"].lower()

"""Integration tests for Adapters FastAPI routes."""

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


def test_validate_url_success() -> None:
    resp = client.post(
        "/api/v1/adapters/validate-url",
        json={"url": "https://www.youtube.com/@veritasium"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["platform"] == "youtube"
    assert data["handle"] == "@veritasium"
    assert data["canonical_url"] == "https://www.youtube.com/@veritasium"


def test_validate_url_invalid_format() -> None:
    resp = client.post(
        "/api/v1/adapters/validate-url",
        json={"url": "http://127.0.0.1/admin"},
    )
    assert resp.status_code == 400
    assert "security" in resp.json()["detail"].lower() or "private" in resp.json()["detail"].lower()


def test_probe_youtube_channel_success() -> None:
    resp = client.post(
        "/api/v1/adapters/probe",
        json={"url": "https://www.youtube.com/@3blue1brown"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["platform"] == "youtube"
    assert data["outcome"] == "ok"
    assert data["account"]["display_name"] == "3Blue1Brown"
    assert data["daily_quota_remaining"] > 0


def test_probe_x_user_success() -> None:
    resp = client.post(
        "/api/v1/adapters/probe",
        json={"url": "https://x.com/elonmusk"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["platform"] == "x"
    assert data["outcome"] == "ok"
    assert data["account"]["username"] == "@elonmusk"


def test_get_quotas() -> None:
    resp = client.get("/api/v1/adapters/quotas")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 2
    platforms = [q["platform"] for q in data]
    assert "youtube" in platforms
    assert "x" in platforms


def test_get_telemetry() -> None:
    resp = client.get("/api/v1/adapters/telemetry")
    assert resp.status_code == 200
    data = resp.json()
    assert "telemetry" in data

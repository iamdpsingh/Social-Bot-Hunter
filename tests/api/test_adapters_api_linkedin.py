"""API Integration tests for LinkedIn adapter endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from services.api.auth import get_current_user
from services.api.main import app
from services.api.schemas import UserResponse


@pytest.fixture(autouse=True)
def auth_override() -> None:
    mock_user = UserResponse(
        id="usr_test_linkedin",
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


def test_api_validate_linkedin_url() -> None:
    client = TestClient(app)
    resp = client.post(
        "/api/v1/adapters/validate-url",
        json={"url": "https://www.linkedin.com/company/tech_corp"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["platform"] == "linkedin"
    assert data["handle"] == "company:tech_corp"
    assert data["canonical_url"] == "https://www.linkedin.com/company/tech_corp"


def test_api_probe_linkedin_organization() -> None:
    client = TestClient(app)
    resp = client.post(
        "/api/v1/adapters/probe",
        json={"url": "https://linkedin.com/company/tech_corp"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["platform"] == "linkedin"
    assert data["outcome"] == "ok"
    assert data["account"]["username"] == "tech-corp"
    assert data["account"]["follower_count"] == 250000


def test_api_probe_linkedin_member() -> None:
    client = TestClient(app)
    resp = client.post(
        "/api/v1/adapters/probe",
        json={"url": "https://linkedin.com/in/satyanadella"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["platform"] == "linkedin"
    assert data["outcome"] == "ok"
    assert data["account"]["username"] == "satyanadella"
    assert data["account"]["follower_count"] == 10500000


def test_api_probe_linkedin_not_found() -> None:
    client = TestClient(app)
    resp = client.post(
        "/api/v1/adapters/probe",
        json={"url": "https://linkedin.com/in/nonexistent_member_123"},
    )
    assert resp.status_code == 400
    assert "not found" in resp.json()["detail"].lower()


def test_api_linkedin_quota_decrement() -> None:
    client = TestClient(app)
    resp = client.get("/api/v1/adapters/quotas")
    assert resp.status_code == 200
    quotas = resp.json()
    li_quota = next(q for q in quotas if q["platform"] == "linkedin")
    assert li_quota["daily_quota_limit"] == 2500
    assert li_quota["status"] == "active"

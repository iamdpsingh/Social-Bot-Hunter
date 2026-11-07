"""Tests for scan diff API router."""

from fastapi.testclient import TestClient
from services.api.auth import get_current_user
from services.api.main import app


def test_diff_router_404_when_scan_missing():
    app.dependency_overrides[get_current_user] = lambda: {
        "id": "usr_test",
        "username": "testuser",
        "role": "analyst",
        "is_active": True,
    }
    try:
        client = TestClient(app)
        res = client.get("/api/v1/diff?scan_a=missing_a&scan_b=missing_b")
        assert res.status_code == 404
        assert "Baseline scan missing_a not found" in res.json()["detail"]
    finally:
        app.dependency_overrides.clear()


def test_diff_registered_in_openapi():
    client = TestClient(app)
    res = client.get("/api/v1/openapi.json")
    assert res.status_code == 200
    assert "/api/v1/diff" in res.json()["paths"]

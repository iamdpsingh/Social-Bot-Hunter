"""Tests for settings and retention API router."""

from fastapi.testclient import TestClient
from services.api.auth import get_current_user
from services.api.main import app


def test_settings_retention_and_quotas():
    app.dependency_overrides[get_current_user] = lambda: {
        "id": "usr_admin",
        "username": "adminuser",
        "role": "admin",
        "is_active": True,
    }
    try:
        client = TestClient(app)
        res_ret = client.get("/api/v1/settings/retention")
        assert res_ret.status_code == 200
        assert "total_scans" in res_ret.json()

        res_quo = client.get("/api/v1/settings/quotas")
        assert res_quo.status_code == 200
        platforms = [p["platform"] for p in res_quo.json()]
        assert "youtube" in platforms
        assert "x" in platforms

        res_purge = client.post("/api/v1/settings/retention/purge", json={"retention_days": 90, "dry_run": True})
        assert res_purge.status_code == 200
        assert res_purge.json()["dry_run"] is True
    finally:
        app.dependency_overrides.clear()

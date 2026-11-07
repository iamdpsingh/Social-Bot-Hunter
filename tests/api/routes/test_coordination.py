"""Tests for coordination API router and client."""

from fastapi.testclient import TestClient
from services.api.main import app


def test_coordination_router_404_for_missing_scan(auth_headers):
    client = TestClient(app)
    res = client.get("/api/v1/scans/missing_scan_999/coordination", headers=auth_headers)
    assert res.status_code == 404
    assert "Scan missing_scan_999 not found" in res.json()["detail"]


def test_coordination_registered_in_openapi():
    client = TestClient(app)
    res = client.get("/api/v1/openapi.json")
    assert res.status_code == 200
    paths = res.json()["paths"]
    assert any("/scans/{scan_id}/coordination" in p for p in paths)

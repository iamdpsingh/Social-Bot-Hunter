from __future__ import annotations

from fastapi.testclient import TestClient
from services.api.main import app

client = TestClient(app)

def test_relationships_unauth_401() -> None:
    res = client.get("/api/v1/scans/dummy_scan/relationships")
    assert res.status_code == 401

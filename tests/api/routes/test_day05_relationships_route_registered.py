from __future__ import annotations

from fastapi.testclient import TestClient
from services.api.main import app

client = TestClient(app)

def test_relationships_route_in_app() -> None:
    # 401 proves the route is matched and intercepted by require_authenticated
    res = client.get("/api/v1/scans/test_scan/relationships")
    assert res.status_code == 401

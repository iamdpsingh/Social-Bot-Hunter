from __future__ import annotations

from fastapi.testclient import TestClient
from services.api.main import app


def test_all_networks_routes_unauthenticated() -> None:
    client = TestClient(app)
    routes = [
        "/api/v1/scans/test_scan/networks/clusters",
        "/api/v1/scans/test_scan/networks/graph",
        "/api/v1/scans/test_scan/networks/nodes/acc/neighbors",
        "/api/v1/scans/test_scan/networks/metrics",
        "/api/v1/scans/test_scan/networks/export",
    ]
    for r in routes:
        res = client.get(r)
        assert res.status_code == 401, f"Route {r} failed to enforce auth: {res.status_code}"

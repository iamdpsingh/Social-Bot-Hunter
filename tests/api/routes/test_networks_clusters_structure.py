from __future__ import annotations

from fastapi.testclient import TestClient
from services.api.main import app


def test_networks_clusters_unauth() -> None:
    client = TestClient(app)
    res = client.get("/api/v1/scans/s_any/networks/clusters")
    assert res.status_code == 401

from __future__ import annotations

from fastapi.testclient import TestClient
from services.api.main import app


def test_get_network_metrics_unauth_401() -> None:
    client = TestClient(app)
    res = client.get("/api/v1/scans/s_1/networks/metrics")
    assert res.status_code == 401

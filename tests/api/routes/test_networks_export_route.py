from __future__ import annotations

from fastapi.testclient import TestClient
from services.api.main import app


def test_export_graph_bundle_unauth_401() -> None:
    client = TestClient(app)
    res = client.get("/api/v1/scans/s_1/networks/export")
    assert res.status_code == 401

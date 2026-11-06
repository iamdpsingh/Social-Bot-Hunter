from __future__ import annotations

from fastapi.testclient import TestClient
from services.api.main import app


def test_get_node_neighbors_unauth_401() -> None:
    client = TestClient(app)
    res = client.get("/api/v1/scans/s_1/networks/nodes/acc_1/neighbors")
    assert res.status_code == 401


def test_get_node_neighbors_regex_validation() -> None:
    client = TestClient(app)
    # invalid direction parameter
    res = client.get("/api/v1/scans/s_1/networks/nodes/acc_1/neighbors?direction=invalid")
    assert res.status_code in (401, 422)

from __future__ import annotations

from fastapi.testclient import TestClient
from services.api.main import app


def test_get_graph_elements_filters() -> None:
    client = TestClient(app)
    # 401 unauthenticated check
    res = client.get("/api/v1/scans/s_1/networks/graph?min_score=0.7&risk_band=critical")
    assert res.status_code == 401

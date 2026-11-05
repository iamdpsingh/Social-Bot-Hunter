from __future__ import annotations

from fastapi.testclient import TestClient
from services.api.main import app

client = TestClient(app)

def test_export_routes_in_app() -> None:
    # 401 proves both routes are matched and intercepted by require_authenticated
    res_csv = client.get("/api/v1/scans/test_scan/export/csv")
    assert res_csv.status_code == 401

    res_json = client.get("/api/v1/scans/test_scan/export/json")
    assert res_json.status_code == 401

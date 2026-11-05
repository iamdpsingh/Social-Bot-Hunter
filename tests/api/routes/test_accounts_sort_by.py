from __future__ import annotations

from fastapi.testclient import TestClient
from services.api.main import app

client = TestClient(app)

def test_accounts_sort_by_unauth_401() -> None:
    res = client.get("/api/v1/scans/scan_1/accounts?sort_by=score_asc")
    assert res.status_code == 401

from __future__ import annotations

from fastapi.testclient import TestClient
from services.api.main import app

client = TestClient(app)

def test_accounts_search_unauth_401() -> None:
    res = client.get("/api/v1/scans/scan_1/accounts?search=bot_army")
    assert res.status_code == 401

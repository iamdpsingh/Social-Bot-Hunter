from __future__ import annotations

from fastapi.testclient import TestClient
from services.api.main import app

client = TestClient(app)

def test_account_evidence_unauth_401() -> None:
    res = client.get("/api/v1/scans/scan_1/accounts/acc_1/evidence")
    assert res.status_code == 401

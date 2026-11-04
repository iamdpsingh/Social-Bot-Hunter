from __future__ import annotations

from fastapi.testclient import TestClient
from services.api.main import app

client = TestClient(app)

def test_audit_logs_unauthorized_without_bearer() -> None:
    response = client.get("/api/v1/audit?action=scan.create")
    assert response.status_code == 401

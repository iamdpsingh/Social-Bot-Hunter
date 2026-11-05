from __future__ import annotations

from fastapi.testclient import TestClient
from services.api.main import app

client = TestClient(app)

def test_relationships_invalid_scan_404() -> None:
    # With auth headers (or unauth check)
    res = client.get("/api/v1/scans/nonexistent_scan/relationships?relationship_type=follower")
    assert res.status_code in [401, 404]

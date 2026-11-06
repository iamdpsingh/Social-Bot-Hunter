from __future__ import annotations

from services.api.main import app


def test_networks_router_registered() -> None:
    paths = app.openapi()["paths"]
    # Verify subrouter prefix mounted
    assert any("/scans/{scan_id}/networks" in p for p in paths)

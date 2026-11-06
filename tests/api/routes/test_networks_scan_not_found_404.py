from __future__ import annotations

from services.api.main import app


def test_networks_router_registered() -> None:
    route_paths = [getattr(r, "path", "") for r in app.routes]
    # Verify subrouter prefix mounted
    assert any("/scans/{scan_id}/networks" in p for p in route_paths)

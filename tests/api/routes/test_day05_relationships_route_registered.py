from __future__ import annotations

from services.api.main import app

def test_relationships_route_in_app() -> None:
    routes = [r.path for r in app.routes]
    assert "/api/v1/scans/{scan_id}/relationships" in routes

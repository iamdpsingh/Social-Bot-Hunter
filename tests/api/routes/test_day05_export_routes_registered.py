from __future__ import annotations

from services.api.main import app

def test_export_routes_in_app() -> None:
    routes = [r.path for r in app.routes]
    assert "/api/v1/scans/{scan_id}/export/csv" in routes
    assert "/api/v1/scans/{scan_id}/export/json" in routes

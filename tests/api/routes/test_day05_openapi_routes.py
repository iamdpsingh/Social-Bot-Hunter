from __future__ import annotations

import json
from pathlib import Path

def test_openapi_contains_day05_routes() -> None:
    doc_path = Path("docs/openapi.json")
    spec = json.loads(doc_path.read_text(encoding="utf-8"))
    paths = spec.get("paths", {})
    assert "/api/v1/scans/{scan_id}/relationships" in paths
    assert "/api/v1/scans/{scan_id}/export/csv" in paths
    assert "/api/v1/scans/{scan_id}/export/json" in paths

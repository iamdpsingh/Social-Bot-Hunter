"""Tests verifying that docs/openapi.json is valid OpenAPI 3.1 and matches FastAPI app schema."""

import json
import unittest
from pathlib import Path

from services.api.main import app

REPO_ROOT = Path(__file__).resolve().parents[2]
OPENAPI_PATH = REPO_ROOT / "docs" / "openapi.json"


class OpenApiSpecTestCase(unittest.TestCase):
    def test_openapi_json_exists_and_is_valid(self):
        self.assertTrue(OPENAPI_PATH.exists(), "docs/openapi.json must exist")
        content = OPENAPI_PATH.read_text(encoding="utf-8")
        data = json.loads(content)

        # Must be OpenAPI 3.1.x
        self.assertIn("openapi", data)
        self.assertTrue(data["openapi"].startswith("3.1"), f"Expected OpenAPI 3.1.x, got {data['openapi']}")

        # Verify title and info
        self.assertEqual(data["info"]["title"], "Social Bot Hunter API")
        self.assertEqual(data["info"]["version"], "0.1.0")

    def test_openapi_json_matches_app_openapi_exactly(self):
        saved_spec = json.loads(OPENAPI_PATH.read_text(encoding="utf-8"))
        live_spec = app.openapi()
        self.assertEqual(saved_spec, live_spec, "docs/openapi.json is out of date. Run 'python3 -m sbh docs --write'")

    def test_required_endpoints_present_in_spec(self):
        spec = json.loads(OPENAPI_PATH.read_text(encoding="utf-8"))
        paths = spec.get("paths", {})

        required_paths = [
            "/api/v1/health",
            "/api/v1/auth/login",
            "/api/v1/auth/token",
            "/api/v1/auth/refresh",
            "/api/v1/auth/logout",
            "/api/v1/auth/me",
            "/api/v1/users",
            "/api/v1/users/{user_id}",
            "/api/v1/audit",
            "/api/v1/audit/{event_id}",
            "/api/v1/capabilities",
            "/api/v1/scans",
            "/api/v1/scans/{scan_id}",
            "/api/v1/scans/{scan_id}/report",
            "/api/v1/scans/{scan_id}/accounts",
            "/api/v1/scans/{scan_id}/networks/clusters",
            "/api/v1/scans/{scan_id}/networks/graph",
            "/api/v1/imports/synthetic-demo",
            "/api/v1/imports/dataset",
        ]

        for p in required_paths:
            self.assertIn(p, paths, f"Path '{p}' missing from OpenAPI specification")

    def test_security_schemes_and_schemas_present(self):
        spec = json.loads(OPENAPI_PATH.read_text(encoding="utf-8"))
        components = spec.get("components", {})
        schemas = components.get("schemas", {})

        required_schemas = [
            "TokenResponse",
            "LoginRequest",
            "RefreshTokenRequest",
            "UserResponse",
            "UserCreateRequest",
            "AuditEventResponse",
            "AuditListResponse",
            "ScanReportResponse",
            "CytoscapeGraphResponse",
            "HealthResponse",
        ]

        for s in required_schemas:
            self.assertIn(s, schemas, f"Schema '{s}' missing from OpenAPI components")


if __name__ == "__main__":
    unittest.main()

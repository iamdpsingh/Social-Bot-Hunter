"""Unit and integration tests for the FastAPI service."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Ensure repo root is on sys.path for services import
REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from fastapi.testclient import TestClient  # noqa: E402
from services.api.auth import create_access_token, hash_password  # noqa: E402
from services.api.deps import get_db  # noqa: E402
from services.api.main import app  # noqa: E402

from sbh.storage import SQLiteDatabase, UserRepository, apply_migrations  # noqa: E402


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        self.db = SQLiteDatabase()
        apply_migrations(self.db)

        self.user_repo = UserRepository(self.db)
        self.admin_user = self.user_repo.create_user(
            username="api_admin",
            hashed_password=hash_password("adminpass123"),
            role="admin",
            full_name="API Admin",
        )
        token, _, _ = create_access_token(
            self.admin_user["id"],
            self.admin_user["username"],
            self.admin_user["role"],
        )
        self.auth_headers = {"Authorization": f"Bearer {token}"}

        def _override_get_db():
            yield self.db

        app.dependency_overrides[get_db] = _override_get_db
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()
        self.db.close()

    def test_root_endpoint(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("docs", data)
        self.assertEqual(data["version"], "0.1.0")
        self.assertIn("X-Trace-ID", res.headers)
        self.assertIn("X-Response-Time-Ms", res.headers)

    def test_health_endpoint(self):
        res = self.client.get("/api/v1/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["database"], "connected")
        self.assertIn("timestamp", data)

    def test_capabilities_endpoint_unauthenticated_returns_401(self):
        res = self.client.get("/api/v1/capabilities")
        self.assertEqual(res.status_code, 401)
        self.assertIn("Authentication required", res.json()["detail"])

    def test_capabilities_endpoint_authenticated(self):
        res = self.client.get("/api/v1/capabilities", headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreater(data["total"], 0)
        self.assertTrue(any(c["platform"] == "x" for c in data["capabilities"]))

    def test_synthetic_demo_import_and_report_pipeline(self):
        # 1. Trigger synthetic demo via API with auth
        demo_res = self.client.post(
            "/api/v1/imports/synthetic-demo?seed=42", headers=self.auth_headers
        )
        self.assertEqual(demo_res.status_code, 200)
        demo_data = demo_res.json()
        scan_id = demo_data["scan_id"]
        self.assertTrue(scan_id)
        self.assertIn(demo_data["status"], ("complete", "partial"))

        # 2. Get scan detail
        scan_res = self.client.get(f"/api/v1/scans/{scan_id}", headers=self.auth_headers)
        self.assertEqual(scan_res.status_code, 200)
        scan = scan_res.json()["scan"]
        self.assertEqual(scan["id"], scan_id)

        # 3. Get scan report
        report_res = self.client.get(
            f"/api/v1/scans/{scan_id}/report?top=10", headers=self.auth_headers
        )
        self.assertEqual(report_res.status_code, 200)
        report = report_res.json()
        self.assertTrue(report["is_synthetic"])
        self.assertGreater(report["total_scored"], 0)
        self.assertGreaterEqual(len(report["clusters"]), 1)

        # 4. Get network graph elements for Cytoscape.js
        graph_res = self.client.get(
            f"/api/v1/scans/{scan_id}/networks/graph?max_nodes=100", headers=self.auth_headers
        )
        self.assertEqual(graph_res.status_code, 200)
        graph = graph_res.json()
        self.assertIn("elements", graph)
        self.assertGreater(graph["node_count"], 0)
        self.assertGreater(graph["edge_count"], 0)
        self.assertTrue(all("data" in n for n in graph["elements"]["nodes"]))
        self.assertTrue(all("data" in e for e in graph["elements"]["edges"]))

        # 5. Delete scan (requires Admin)
        del_res = self.client.delete(f"/api/v1/scans/{scan_id}", headers=self.auth_headers)
        self.assertEqual(del_res.status_code, 200)
        self.assertEqual(del_res.json()["status"], "deleted")

        # 6. Verify scan is gone
        get_again = self.client.get(f"/api/v1/scans/{scan_id}", headers=self.auth_headers)
        self.assertEqual(get_again.status_code, 404)


if __name__ == "__main__":
    unittest.main()

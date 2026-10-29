"""Unit and integration tests for the FastAPI service."""

import sys
import unittest
from pathlib import Path

# Ensure repo root is on sys.path for services import
REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from fastapi.testclient import TestClient  # noqa: E402
from services.api.deps import get_db  # noqa: E402
from services.api.main import app  # noqa: E402

from sbh.storage import SQLiteDatabase, apply_migrations  # noqa: E402


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        self.db = SQLiteDatabase()
        apply_migrations(self.db)

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

    def test_health_endpoint(self):
        res = self.client.get("/api/v1/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["database"], "connected")

    def test_capabilities_endpoint(self):
        res = self.client.get("/api/v1/capabilities")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreater(data["total"], 0)
        self.assertTrue(any(c["platform"] == "x" for c in data["capabilities"]))

    def test_synthetic_demo_import_and_report_pipeline(self):
        # 1. Trigger synthetic demo via API
        demo_res = self.client.post("/api/v1/imports/synthetic-demo?seed=42")
        self.assertEqual(demo_res.status_code, 200)
        demo_data = demo_res.json()
        scan_id = demo_data["scan_id"]
        self.assertTrue(scan_id)
        self.assertIn(demo_data["status"], ("complete", "partial"))

        # 2. Get scan detail
        scan_res = self.client.get(f"/api/v1/scans/{scan_id}")
        self.assertEqual(scan_res.status_code, 200)
        scan = scan_res.json()["scan"]
        self.assertEqual(scan["id"], scan_id)

        # 3. Get scan report
        report_res = self.client.get(f"/api/v1/scans/{scan_id}/report?top=10")
        self.assertEqual(report_res.status_code, 200)
        report = report_res.json()
        self.assertTrue(report["is_synthetic"])
        self.assertGreater(report["total_scored"], 0)
        self.assertGreaterEqual(len(report["clusters"]), 1)

        # 4. Get network graph elements for Cytoscape.js
        graph_res = self.client.get(f"/api/v1/scans/{scan_id}/networks/graph?max_nodes=100")
        self.assertEqual(graph_res.status_code, 200)
        graph = graph_res.json()
        self.assertIn("elements", graph)
        self.assertGreater(graph["node_count"], 0)
        self.assertGreater(graph["edge_count"], 0)
        self.assertTrue(all("data" in n for n in graph["elements"]["nodes"]))
        self.assertTrue(all("data" in e for e in graph["elements"]["edges"]))

        # 5. Delete scan
        del_res = self.client.delete(f"/api/v1/scans/{scan_id}")
        self.assertEqual(del_res.status_code, 200)
        self.assertEqual(del_res.json()["status"], "deleted")

        # 6. Verify scan is gone
        get_again = self.client.get(f"/api/v1/scans/{scan_id}")
        self.assertEqual(get_again.status_code, 404)


if __name__ == "__main__":
    unittest.main()

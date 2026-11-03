from __future__ import annotations
import unittest
from services.api.schemas import ScanProgressResponse

class RouteTest_test_scans_progress_response_schema(unittest.TestCase):
    def test_schema_types(self) -> None:
        p = ScanProgressResponse(scan_id="s1", status="running", stage="ingest_edges", progress_pct=45.0)
        self.assertEqual(p.progress_pct, 45.0)
        self.assertEqual(p.stage, "ingest_edges")

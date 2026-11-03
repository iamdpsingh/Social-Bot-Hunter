from __future__ import annotations

import unittest

from services.api.schemas import ScanRetryResponse


class RouteTest_test_scans_retry_response_schema(unittest.TestCase):
    def test_retry_schema(self) -> None:
        r = ScanRetryResponse(scan_id="s1")
        self.assertEqual(r.scan_id, "s1")
        self.assertEqual(r.status, "pending")
        self.assertIn("retry", r.message)

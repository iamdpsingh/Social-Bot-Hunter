from __future__ import annotations

import unittest

from services.api.schemas import ScanCancelResponse


class RouteTest_test_scans_cancel_response_schema(unittest.TestCase):
    def test_schema_fields(self) -> None:
        r = ScanCancelResponse(scan_id="s1")
        self.assertEqual(r.scan_id, "s1")
        self.assertEqual(r.status, "cancelled")
        self.assertIn("cancellation", r.message)

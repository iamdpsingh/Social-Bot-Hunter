from __future__ import annotations

import unittest

from services.api.routers.scans import router


class RouteTest_test_scans_events_content_type_sse(unittest.TestCase):
    def test_route_registered(self) -> None:
        routes = [r.path for r in router.routes]
        self.assertIn("/scans/{scan_id}/events", routes)

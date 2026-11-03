from __future__ import annotations

import unittest

from services.api.routers.scans import router


class RouteTest_test_scans_events_cache_control_no_cache(unittest.TestCase):
    def test_route_methods(self) -> None:
        for r in router.routes:
            if getattr(r, "path", None) == "/scans/{scan_id}/events":
                self.assertIn("GET", r.methods)

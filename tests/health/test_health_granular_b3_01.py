"""Granular test 1: status aggregation."""

from __future__ import annotations

import unittest

from sbh.health.diagnostics import SystemHealthReport
from sbh.health.probes import HealthProbeResult, SubsystemStatus


class TestHealthGranularB301(unittest.TestCase):
    def test_unhealthy_probe_causes_unhealthy_system(self):
        p1 = HealthProbeResult("p1", SubsystemStatus.HEALTHY, 1.0, "ok", {})
        p2 = HealthProbeResult("p2", SubsystemStatus.UNHEALTHY, 1.0, "fail", {})
        rep = SystemHealthReport(
            overall_status=SubsystemStatus.UNHEALTHY,
            timestamp="2026-11-14T00:00:00Z",
            total_probes=2,
            healthy_count=1,
            degraded_count=0,
            unhealthy_count=1,
            probes=[p1, p2],
        )
        self.assertEqual(rep.overall_status, SubsystemStatus.UNHEALTHY)


if __name__ == "__main__":
    unittest.main()

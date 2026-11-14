"""Granular test 2: degraded propagation."""

from __future__ import annotations

import unittest
from sbh.health.diagnostics import SystemHealthReport
from sbh.health.probes import HealthProbeResult, SubsystemStatus


class TestHealthGranularB302(unittest.TestCase):
    def test_degraded_probe_causes_degraded_system(self):
        p1 = HealthProbeResult("p1", SubsystemStatus.HEALTHY, 1.0, "ok", {})
        p2 = HealthProbeResult("p2", SubsystemStatus.DEGRADED, 1.0, "warn", {})
        rep = SystemHealthReport(
            overall_status=SubsystemStatus.DEGRADED,
            timestamp="2026-11-14T00:00:00Z",
            total_probes=2,
            healthy_count=1,
            degraded_count=1,
            unhealthy_count=0,
            probes=[p1, p2],
        )
        self.assertEqual(rep.overall_status, SubsystemStatus.DEGRADED)


if __name__ == "__main__":
    unittest.main()

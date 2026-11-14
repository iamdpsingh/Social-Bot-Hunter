"""Granular test 3: latency is non-negative."""

from __future__ import annotations

import unittest
from sbh.health.probes import HealthProbeRunner


class TestHealthGranularB303(unittest.TestCase):
    def test_sqlite_probe_positive_latency(self):
        res = HealthProbeRunner.check_sqlite()
        self.assertGreaterEqual(res.latency_ms, 0.0)


if __name__ == "__main__":
    unittest.main()

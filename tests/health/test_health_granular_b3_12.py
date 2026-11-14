"""Granular test 12: probe count arithmetic."""

from __future__ import annotations

import unittest
from sbh.health.diagnostics import run_full_system_diagnostics


class TestHealthGranularB312(unittest.TestCase):
    def test_counts_sum_to_total(self):
        rep = run_full_system_diagnostics()
        sum_counts = rep.healthy_count + rep.degraded_count + rep.unhealthy_count
        self.assertEqual(rep.total_probes, sum_counts)


if __name__ == "__main__":
    unittest.main()

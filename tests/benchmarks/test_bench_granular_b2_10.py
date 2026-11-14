"""Granular benchmark test 10: outlier resistance."""

from __future__ import annotations

import unittest

from sbh.benchmarks.metrics import calculate_percentiles


class TestBenchGranularB210(unittest.TestCase):
    def test_outlier_does_not_affect_p50(self):
        durations = [1.0] * 98 + [1000.0] * 2
        pcts = calculate_percentiles(durations)
        self.assertEqual(pcts["p50"], 1.0)
        self.assertEqual(pcts["p90"], 1.0)
        self.assertEqual(pcts["p99"], 1000.0)


if __name__ == "__main__":
    unittest.main()

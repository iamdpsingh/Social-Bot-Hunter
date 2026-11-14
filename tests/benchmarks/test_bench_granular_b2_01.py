"""Granular benchmark test 1: single iteration duration."""

from __future__ import annotations

import unittest
from sbh.benchmarks.metrics import BenchmarkMetrics


class TestBenchGranularB201(unittest.TestCase):
    def test_single_iteration(self):
        m = BenchmarkMetrics.from_durations("single", [5.5])
        self.assertEqual(m.iterations, 1)
        self.assertEqual(m.min_ms, 5.5)
        self.assertEqual(m.max_ms, 5.5)
        self.assertEqual(m.p99_ms, 5.5)


if __name__ == "__main__":
    unittest.main()

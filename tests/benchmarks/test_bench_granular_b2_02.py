"""Granular benchmark test 2: zero durations."""

from __future__ import annotations

import unittest

from sbh.benchmarks.metrics import BenchmarkMetrics


class TestBenchGranularB202(unittest.TestCase):
    def test_empty_durations(self):
        m = BenchmarkMetrics.from_durations("empty", [])
        self.assertEqual(m.iterations, 0)
        self.assertEqual(m.throughput_ops_sec, 0.0)
        self.assertEqual(m.p50_ms, 0.0)


if __name__ == "__main__":
    unittest.main()

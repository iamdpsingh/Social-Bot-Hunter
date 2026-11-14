"""Granular benchmark test 3: throughput math."""

from __future__ import annotations

import unittest

from sbh.benchmarks.metrics import BenchmarkMetrics


class TestBenchGranularB203(unittest.TestCase):
    def test_high_throughput_calculation(self):
        # 1000 items in 1000 ms total = 1000 ops/s
        durations = [1.0] * 1000
        m = BenchmarkMetrics.from_durations("throughput_test", durations)
        self.assertEqual(m.throughput_ops_sec, 1000.0)


if __name__ == "__main__":
    unittest.main()

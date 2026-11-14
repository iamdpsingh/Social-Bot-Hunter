"""Granular benchmark test 11: mean calculation."""

from __future__ import annotations

import unittest

from sbh.benchmarks.metrics import BenchmarkMetrics


class TestBenchGranularB211(unittest.TestCase):
    def test_mean_accuracy(self):
        m = BenchmarkMetrics.from_durations("mean_test", [10.0, 20.0, 30.0])
        self.assertEqual(m.mean_ms, 20.0)


if __name__ == "__main__":
    unittest.main()

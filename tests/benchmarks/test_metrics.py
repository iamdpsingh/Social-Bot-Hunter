"""Tests for calculate_percentiles and BenchmarkMetrics aggregation."""

from __future__ import annotations

import unittest

from sbh.benchmarks.metrics import BenchmarkMetrics, calculate_percentiles


class TestBenchmarkMetrics(unittest.TestCase):
    def test_calculate_percentiles_regular_sequence(self):
        # 100 values from 1.0 to 100.0
        durations = [float(i) for i in range(1, 101)]
        pcts = calculate_percentiles(durations)
        self.assertEqual(pcts["p50"], 50.0)
        self.assertEqual(pcts["p90"], 90.0)
        self.assertEqual(pcts["p95"], 95.0)
        self.assertEqual(pcts["p99"], 99.0)

    def test_calculate_percentiles_empty(self):
        pcts = calculate_percentiles([])
        self.assertEqual(pcts["p50"], 0.0)
        self.assertEqual(pcts["p99"], 0.0)

    def test_metrics_from_durations(self):
        durations = [10.0, 20.0, 30.0, 40.0, 50.0]
        m = BenchmarkMetrics.from_durations("sample_task", durations)
        self.assertEqual(m.name, "sample_task")
        self.assertEqual(m.iterations, 5)
        self.assertEqual(m.min_ms, 10.0)
        self.assertEqual(m.max_ms, 50.0)
        self.assertEqual(m.mean_ms, 30.0)
        self.assertGreater(m.throughput_ops_sec, 0.0)


if __name__ == "__main__":
    unittest.main()

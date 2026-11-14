"""Granular benchmark test 5: warmup run counting."""

from __future__ import annotations

import unittest

from sbh.benchmarks.runner import BenchmarkHarness


class TestBenchGranularB205(unittest.TestCase):
    def test_warmup_runs_executed(self):
        harness = BenchmarkHarness(warmup_runs=5)
        calls = {"count": 0}

        def fn():
            calls["count"] += 1

        res = harness.run_callable("call_count", fn, iterations=10, sla_p99_ms=50.0)
        self.assertEqual(calls["count"], 15)  # 5 warmup + 10 benchmark
        self.assertEqual(res.metrics.iterations, 10)


if __name__ == "__main__":
    unittest.main()

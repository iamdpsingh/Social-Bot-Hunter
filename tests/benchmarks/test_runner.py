"""Tests for BenchmarkHarness execution and built-in benchmarks."""

from __future__ import annotations

import unittest

from sbh.benchmarks.runner import BenchmarkHarness


class TestBenchmarkRunner(unittest.TestCase):
    def test_run_callable_passes_sla(self):
        harness = BenchmarkHarness(warmup_runs=2)
        counter = {"count": 0}

        def simple_add():
            counter["count"] += 1

        result = harness.run_callable("simple_add", simple_add, iterations=50, sla_p99_ms=10.0)
        self.assertTrue(result.passed_sla)
        self.assertEqual(result.metrics.iterations, 50)
        self.assertLess(result.metrics.p99_ms, 10.0)

    def test_run_sqlite_in_memory_benchmark(self):
        harness = BenchmarkHarness(warmup_runs=2)
        res = harness.run_sqlite_in_memory_benchmark(iterations=100)
        self.assertTrue(res.passed_sla)
        self.assertEqual(res.task_name, "sqlite_in_memory_query")

    def test_run_simhash_benchmark(self):
        harness = BenchmarkHarness(warmup_runs=2)
        res = harness.run_simhash_benchmark(iterations=100)
        self.assertTrue(res.passed_sla)
        self.assertEqual(res.task_name, "simhash_text_hashing")


if __name__ == "__main__":
    unittest.main()

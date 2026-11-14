"""Granular benchmark test 9: SQLite insert throughput."""

from __future__ import annotations

import sqlite3
import unittest

from sbh.benchmarks.runner import BenchmarkHarness


class TestBenchGranularB209(unittest.TestCase):
    def test_sqlite_insert_benchmark(self):
        conn = sqlite3.connect(":memory:")
        conn.execute("CREATE TABLE records (id INTEGER PRIMARY KEY, val TEXT)")
        harness = BenchmarkHarness(warmup_runs=1)

        counter = [0]

        def insert_row():
            counter[0] += 1
            conn.execute("INSERT INTO records VALUES (?, ?)", (counter[0], "val"))

        res = harness.run_callable("sqlite_insert", insert_row, iterations=50, sla_p99_ms=5.0)
        self.assertTrue(res.passed_sla)
        conn.close()


if __name__ == "__main__":
    unittest.main()

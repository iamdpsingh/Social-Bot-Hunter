"""Execution harness for running micro-benchmarks with warmup runs."""

from __future__ import annotations

import sqlite3
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from sbh.benchmarks.metrics import BenchmarkMetrics
from sbh.detection.simhash import compute_simhash


@dataclass
class BenchmarkTaskResult:
    """Result of an individual benchmark task."""

    task_name: str
    metrics: BenchmarkMetrics
    passed_sla: bool
    sla_p99_ms: float


class BenchmarkHarness:
    """Harness to execute and evaluate micro-benchmarks against latency SLAs."""

    def __init__(self, warmup_runs: int = 5):
        self.warmup_runs = warmup_runs

    def run_callable(
        self,
        name: str,
        fn: Callable[[], Any],
        iterations: int = 100,
        sla_p99_ms: float = 50.0,
    ) -> BenchmarkTaskResult:
        """Run a callable function repeatedly and compute latency metrics."""
        for _ in range(self.warmup_runs):
            fn()

        durations: list[float] = []
        for _ in range(iterations):
            start = time.perf_counter()
            fn()
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            durations.append(elapsed_ms)

        metrics = BenchmarkMetrics.from_durations(name, durations)
        passed_sla = metrics.p99_ms <= sla_p99_ms

        return BenchmarkTaskResult(
            task_name=name,
            metrics=metrics,
            passed_sla=passed_sla,
            sla_p99_ms=sla_p99_ms,
        )

    def run_sqlite_in_memory_benchmark(self, iterations: int = 200) -> BenchmarkTaskResult:
        """Benchmark in-memory SQLite table lookup."""
        conn = sqlite3.connect(":memory:")
        conn.execute("CREATE TABLE accounts (id TEXT PRIMARY KEY, score REAL)")
        conn.execute("INSERT INTO accounts VALUES ('acc1', 0.85)")

        def query_account() -> Any:
            cur = conn.execute("SELECT score FROM accounts WHERE id = 'acc1'")
            return cur.fetchone()

        res = self.run_callable("sqlite_in_memory_query", query_account, iterations=iterations, sla_p99_ms=5.0)
        conn.close()
        return res

    def run_simhash_benchmark(self, iterations: int = 500) -> BenchmarkTaskResult:
        """Benchmark SimHash text hashing."""
        sample_text = "Claim your free crypto reward token right now at verified-crypto-protocol.org! 🚀"

        def hash_text() -> int:
            return compute_simhash(sample_text)

        return self.run_callable("simhash_text_hashing", hash_text, iterations=iterations, sla_p99_ms=1.0)

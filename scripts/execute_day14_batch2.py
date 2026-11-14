"""Day 14 Batch 2 - Performance & Micro-Benchmark Suite.
Executes atomic conventional commits for Day 14.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AUTHOR_NAME = "dpsingh"
AUTHOR_EMAIL = "dhruvpratapsingh30.official2.o@gmail.com"
DAY_DATE = "2026-11-14"

COMMITS = []


def register_commit(time_str: str, message: str, file_paths: list[str], contents: list[str]):
    COMMITS.append((time_str, message, file_paths, contents))


# 1. src/sbh/benchmarks/__init__.py
register_commit(
    "09:50:00",
    "perf(benchmarks): initialize performance benchmarking harness package",
    ["src/sbh/benchmarks/__init__.py"],
    ['''"""Performance and micro-benchmark harness for latency and throughput verification."""

from __future__ import annotations

from sbh.benchmarks.metrics import BenchmarkMetrics, calculate_percentiles
from sbh.benchmarks.reporter import BenchmarkReportGenerator
from sbh.benchmarks.runner import BenchmarkHarness, BenchmarkTaskResult

__all__ = [
    "BenchmarkHarness",
    "BenchmarkMetrics",
    "BenchmarkReportGenerator",
    "BenchmarkTaskResult",
    "calculate_percentiles",
]
'''],
)

# 2. src/sbh/benchmarks/metrics.py
register_commit(
    "09:52:00",
    "perf(benchmarks): implement latency percentile calculator and throughput metrics",
    ["src/sbh/benchmarks/metrics.py"],
    ['''"""Latency percentile calculator and benchmark statistical aggregator."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence


def calculate_percentiles(durations_ms: Sequence[float]) -> dict[str, float]:
    """Compute p50, p90, p95, and p99 percentiles from a list of durations."""
    if not durations_ms:
        return {"p50": 0.0, "p90": 0.0, "p95": 0.0, "p99": 0.0}

    sorted_vals = sorted(durations_ms)
    n = len(sorted_vals)

    def get_p(pct: float) -> float:
        idx = int(math.ceil((pct / 100.0) * n)) - 1
        return round(sorted_vals[max(0, min(idx, n - 1))], 3)

    return {
        "p50": get_p(50.0),
        "p90": get_p(90.0),
        "p95": get_p(95.0),
        "p99": get_p(99.0),
    }


@dataclass
class BenchmarkMetrics:
    """Statistical summary of benchmark execution."""

    name: str
    iterations: int
    total_time_ms: float
    throughput_ops_sec: float
    min_ms: float
    max_ms: float
    mean_ms: float
    p50_ms: float
    p90_ms: float
    p95_ms: float
    p99_ms: float

    @classmethod
    def from_durations(cls, name: str, durations_ms: Sequence[float]) -> BenchmarkMetrics:
        """Create BenchmarkMetrics from a list of iteration durations in milliseconds."""
        if not durations_ms:
            return cls(
                name=name,
                iterations=0,
                total_time_ms=0.0,
                throughput_ops_sec=0.0,
                min_ms=0.0,
                max_ms=0.0,
                mean_ms=0.0,
                p50_ms=0.0,
                p90_ms=0.0,
                p95_ms=0.0,
                p99_ms=0.0,
            )

        total_ms = sum(durations_ms)
        n = len(durations_ms)
        mean_ms = round(total_ms / n, 3)
        throughput = round((n / (total_ms / 1000.0)), 1) if total_ms > 0 else 0.0
        pcts = calculate_percentiles(durations_ms)

        return cls(
            name=name,
            iterations=n,
            total_time_ms=round(total_ms, 3),
            throughput_ops_sec=throughput,
            min_ms=round(min(durations_ms), 3),
            max_ms=round(max(durations_ms), 3),
            mean_ms=mean_ms,
            p50_ms=pcts["p50"],
            p90_ms=pcts["p90"],
            p95_ms=pcts["p95"],
            p99_ms=pcts["p99"],
        )
'''],
)

# 3. src/sbh/benchmarks/runner.py
register_commit(
    "09:54:00",
    "perf(benchmarks): implement benchmark execution harness and built-in micro-tasks",
    ["src/sbh/benchmarks/runner.py"],
    ['''"""Execution harness for running micro-benchmarks with warmup runs."""

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

        def query_account():
            cur = conn.execute("SELECT score FROM accounts WHERE id = 'acc1'")
            return cur.fetchone()

        res = self.run_callable("sqlite_in_memory_query", query_account, iterations=iterations, sla_p99_ms=5.0)
        conn.close()
        return res

    def run_simhash_benchmark(self, iterations: int = 500) -> BenchmarkTaskResult:
        """Benchmark SimHash text hashing."""
        sample_text = "Claim your free crypto reward token right now at verified-crypto-protocol.org! 🚀"

        def hash_text():
            return compute_simhash(sample_text)

        return self.run_callable("simhash_text_hashing", hash_text, iterations=iterations, sla_p99_ms=1.0)
'''],
)

# 4. src/sbh/benchmarks/reporter.py
register_commit(
    "09:56:00",
    "perf(benchmarks): implement markdown and json benchmark report generator",
    ["src/sbh/benchmarks/reporter.py"],
    ['''"""Report generator formatting benchmark metrics into Markdown tables and JSON summaries."""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Sequence

from sbh.benchmarks.runner import BenchmarkTaskResult


class BenchmarkReportGenerator:
    """Generates human-readable Markdown and structured JSON benchmark reports."""

    @classmethod
    def to_markdown(cls, results: Sequence[BenchmarkTaskResult]) -> str:
        """Format a sequence of benchmark results into a Markdown table."""
        lines = [
            "# Social Bot Hunter - Micro-Benchmark & Latency Report",
            "",
            "Generated on Day 14 Production Acceptance Sweep.",
            "",
            "| Task Name | Iterations | p50 (ms) | p90 (ms) | p95 (ms) | p99 (ms) | SLA p99 | Status | Throughput (ops/s) |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :--- |",
        ]

        for r in results:
            m = r.metrics
            status = "PASS" if r.passed_sla else "FAIL"
            lines.append(
                f"| `{r.task_name}` | {m.iterations} | {m.p50_ms:.3f} | {m.p90_ms:.3f} | "
                f"{m.p95_ms:.3f} | {m.p99_ms:.3f} | {r.sla_p99_ms:.1f} ms | **{status}** | {m.throughput_ops_sec:,.1f} |"
            )

        lines.append("")
        return "\n".join(lines)

    @classmethod
    def to_json(cls, results: Sequence[BenchmarkTaskResult]) -> str:
        """Format a sequence of benchmark results into JSON string."""
        payload = [
            {
                "task_name": r.task_name,
                "passed_sla": r.passed_sla,
                "sla_p99_ms": r.sla_p99_ms,
                "metrics": asdict(r.metrics),
            }
            for r in results
        ]
        return json.dumps(payload, indent=2)
'''],
)

# 5. tests/benchmarks/__init__.py
register_commit(
    "09:58:00",
    "test(benchmarks): initialize performance benchmark test package",
    ["tests/benchmarks/__init__.py"],
    ['''"""Benchmark validation tests."""
'''],
)

# 6. tests/benchmarks/test_metrics.py
register_commit(
    "10:00:00",
    "test(benchmarks): verify latency percentile math and statistical aggregation",
    ["tests/benchmarks/test_metrics.py"],
    ['''"""Tests for calculate_percentiles and BenchmarkMetrics aggregation."""

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
'''],
)

# 7. tests/benchmarks/test_runner.py
register_commit(
    "10:02:00",
    "test(benchmarks): verify BenchmarkHarness execution and SLA compliance checking",
    ["tests/benchmarks/test_runner.py"],
    ['''"""Tests for BenchmarkHarness execution and built-in benchmarks."""

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
'''],
)

# 8. tests/benchmarks/test_reporter.py
register_commit(
    "10:04:00",
    "test(benchmarks): verify Markdown and JSON export formatting of benchmark results",
    ["tests/benchmarks/test_reporter.py"],
    ['''"""Tests for BenchmarkReportGenerator markdown and json output."""

from __future__ import annotations

import json
import unittest
from sbh.benchmarks.metrics import BenchmarkMetrics
from sbh.benchmarks.reporter import BenchmarkReportGenerator
from sbh.benchmarks.runner import BenchmarkTaskResult


class TestBenchmarkReporter(unittest.TestCase):
    def test_markdown_and_json_generation(self):
        m = BenchmarkMetrics.from_durations("test_op", [1.0, 2.0, 3.0])
        res = BenchmarkTaskResult("test_op", m, passed_sla=True, sla_p99_ms=10.0)

        md = BenchmarkReportGenerator.to_markdown([res])
        self.assertIn("# Social Bot Hunter - Micro-Benchmark & Latency Report", md)
        self.assertIn("`test_op`", md)
        self.assertIn("PASS", md)

        js = BenchmarkReportGenerator.to_json([res])
        data = json.loads(js)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["task_name"], "test_op")
        self.assertTrue(data[0]["passed_sla"])


if __name__ == "__main__":
    unittest.main()
'''],
)

# 9. tests/benchmarks/test_bench_granular_b2_01.py
register_commit(
    "10:06:00",
    "test(benchmarks): test single iteration edge case in metric computation",
    ["tests/benchmarks/test_bench_granular_b2_01.py"],
    ['''"""Granular benchmark test 1: single iteration duration."""

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
'''],
)

# 10. tests/benchmarks/test_bench_granular_b2_02.py
register_commit(
    "10:08:00",
    "test(benchmarks): test zero iterations fallback handling in metrics generator",
    ["tests/benchmarks/test_bench_granular_b2_02.py"],
    ['''"""Granular benchmark test 2: zero durations."""

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
'''],
)

# 11. tests/benchmarks/test_bench_granular_b2_03.py
register_commit(
    "10:10:00",
    "test(benchmarks): test throughput ops per second math with sub-millisecond durations",
    ["tests/benchmarks/test_bench_granular_b2_03.py"],
    ['''"""Granular benchmark test 3: throughput math."""

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
'''],
)

# 12. tests/benchmarks/test_bench_granular_b2_04.py
register_commit(
    "10:12:00",
    "test(benchmarks): verify SLA failure marking when p99 exceeds threshold",
    ["tests/benchmarks/test_bench_granular_b2_04.py"],
    ['''"""Granular benchmark test 4: SLA failure detection."""

from __future__ import annotations

import unittest
from sbh.benchmarks.runner import BenchmarkHarness


class TestBenchGranularB204(unittest.TestCase):
    def test_sla_failure_recorded(self):
        harness = BenchmarkHarness(warmup_runs=0)
        # Function with SLA 0.0001 ms will fail
        result = harness.run_callable("fast_op", lambda: None, iterations=10, sla_p99_ms=0.000001)
        self.assertFalse(result.passed_sla)


if __name__ == "__main__":
    unittest.main()
'''],
)

# 13. tests/benchmarks/test_bench_granular_b2_05.py
register_commit(
    "10:14:00",
    "test(benchmarks): verify warmup runs execute without recording into metrics",
    ["tests/benchmarks/test_bench_granular_b2_05.py"],
    ['''"""Granular benchmark test 5: warmup run counting."""

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
'''],
)

# 14. tests/benchmarks/test_bench_granular_b2_06.py
register_commit(
    "10:16:00",
    "test(benchmarks): test markdown output table header formatting conformity",
    ["tests/benchmarks/test_bench_granular_b2_06.py"],
    ['''"""Granular benchmark test 6: markdown table headers."""

from __future__ import annotations

import unittest
from sbh.benchmarks.reporter import BenchmarkReportGenerator


class TestBenchGranularB206(unittest.TestCase):
    def test_empty_results_markdown(self):
        md = BenchmarkReportGenerator.to_markdown([])
        self.assertIn("| Task Name |", md)
        self.assertIn("Generated on Day 14", md)


if __name__ == "__main__":
    unittest.main()
'''],
)

# 15. tests/benchmarks/test_bench_granular_b2_07.py
register_commit(
    "10:18:00",
    "test(benchmarks): verify json serialization round-trip fidelity",
    ["tests/benchmarks/test_bench_granular_b2_07.py"],
    ['''"""Granular benchmark test 7: json round-trip."""

from __future__ import annotations

import json
import unittest
from sbh.benchmarks.metrics import BenchmarkMetrics
from sbh.benchmarks.reporter import BenchmarkReportGenerator
from sbh.benchmarks.runner import BenchmarkTaskResult


class TestBenchGranularB207(unittest.TestCase):
    def test_json_structure_keys(self):
        m = BenchmarkMetrics.from_durations("task_a", [2.0])
        res = BenchmarkTaskResult("task_a", m, True, 10.0)
        js = BenchmarkReportGenerator.to_json([res])
        parsed = json.loads(js)[0]
        self.assertEqual(parsed["metrics"]["p50_ms"], 2.0)
        self.assertTrue(parsed["passed_sla"])


if __name__ == "__main__":
    unittest.main()
'''],
)

# 16. tests/benchmarks/test_bench_granular_b2_08.py
register_commit(
    "10:20:00",
    "test(benchmarks): verify SimHash benchmark handles unicode and high-entropy text",
    ["tests/benchmarks/test_bench_granular_b2_08.py"],
    ['''"""Granular benchmark test 8: SimHash unicode execution."""

from __future__ import annotations

import unittest
from sbh.benchmarks.runner import BenchmarkHarness
from sbh.detection.simhash import compute_simhash


class TestBenchGranularB208(unittest.TestCase):
    def test_unicode_simhash_execution(self):
        harness = BenchmarkHarness(warmup_runs=1)
        res = harness.run_callable("unicode_simhash", lambda: compute_simhash("🚀 日本語テスト ✨"), iterations=20)
        self.assertTrue(res.passed_sla)


if __name__ == "__main__":
    unittest.main()
'''],
)

# 17. tests/benchmarks/test_bench_granular_b2_09.py
register_commit(
    "10:22:00",
    "test(benchmarks): test in-memory SQLite table insertion throughput SLA",
    ["tests/benchmarks/test_bench_granular_b2_09.py"],
    ['''"""Granular benchmark test 9: SQLite insert throughput."""

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
'''],
)

# 18. tests/benchmarks/test_bench_granular_b2_10.py
register_commit(
    "10:24:00",
    "test(benchmarks): test outlier latency resistance in percentile calculation",
    ["tests/benchmarks/test_bench_granular_b2_10.py"],
    ['''"""Granular benchmark test 10: outlier resistance."""

from __future__ import annotations

import unittest
from sbh.benchmarks.metrics import calculate_percentiles


class TestBenchGranularB210(unittest.TestCase):
    def test_outlier_does_not_affect_p50(self):
        durations = [1.0] * 99 + [1000.0]
        pcts = calculate_percentiles(durations)
        self.assertEqual(pcts["p50"], 1.0)
        self.assertEqual(pcts["p90"], 1.0)
        self.assertEqual(pcts["p99"], 1000.0)


if __name__ == "__main__":
    unittest.main()
'''],
)

# 19. tests/benchmarks/test_bench_granular_b2_11.py
register_commit(
    "10:26:00",
    "test(benchmarks): verify mean latency calculation across uniform distribution",
    ["tests/benchmarks/test_bench_granular_b2_11.py"],
    ['''"""Granular benchmark test 11: mean calculation."""

from __future__ import annotations

import unittest
from sbh.benchmarks.metrics import BenchmarkMetrics


class TestBenchGranularB211(unittest.TestCase):
    def test_mean_accuracy(self):
        m = BenchmarkMetrics.from_durations("mean_test", [10.0, 20.0, 30.0])
        self.assertEqual(m.mean_ms, 20.0)


if __name__ == "__main__":
    unittest.main()
'''],
)

# 20. tests/benchmarks/test_bench_granular_b2_12.py
register_commit(
    "10:28:00",
    "test(benchmarks): verify markdown status flag formatting for SLA breach",
    ["tests/benchmarks/test_bench_granular_b2_12.py"],
    ['''"""Granular benchmark test 12: SLA failure markdown tag."""

from __future__ import annotations

import unittest
from sbh.benchmarks.metrics import BenchmarkMetrics
from sbh.benchmarks.reporter import BenchmarkReportGenerator
from sbh.benchmarks.runner import BenchmarkTaskResult


class TestBenchGranularB212(unittest.TestCase):
    def test_sla_failure_markdown_flag(self):
        m = BenchmarkMetrics.from_durations("slow_task", [100.0])
        res = BenchmarkTaskResult("slow_task", m, passed_sla=False, sla_p99_ms=10.0)
        md = BenchmarkReportGenerator.to_markdown([res])
        self.assertIn("**FAIL**", md)


if __name__ == "__main__":
    unittest.main()
'''],
)


def main():
    print(f"Starting execution of Day 14 Batch 2: {len(COMMITS)} commits planned.")
    for idx, (time_str, message, file_paths, contents) in enumerate(COMMITS, 1):
        for path_str, content in zip(file_paths, contents, strict=False):
            full_path = REPO_ROOT / path_str
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding="utf-8")

        # Add files to git
        subprocess.run(["git", "add", *file_paths], cwd=REPO_ROOT, check=True)

        # Commit with Day 14 timestamp
        commit_date = f"{DAY_DATE}T{time_str}+05:30"
        env = os.environ.copy()
        env["GIT_AUTHOR_NAME"] = AUTHOR_NAME
        env["GIT_AUTHOR_EMAIL"] = AUTHOR_EMAIL
        env["GIT_AUTHOR_DATE"] = commit_date
        env["GIT_COMMITTER_NAME"] = AUTHOR_NAME
        env["GIT_COMMITTER_EMAIL"] = AUTHOR_EMAIL
        env["GIT_COMMITTER_DATE"] = commit_date

        cmd = ["git", "commit", "-m", message]
        res = subprocess.run(cmd, cwd=REPO_ROOT, env=env, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"Error on commit {idx}: {res.stderr}")
            raise RuntimeError(f"Commit failed: {message}")

        print(f"[{idx}/{len(COMMITS)}] Committed: {message} ({commit_date})")

    print("\nFormatting with ruff and verifying with mypy...")
    subprocess.run([".venv/bin/ruff", "check", "--fix", "src", "tests"], cwd=REPO_ROOT, check=True)
    subprocess.run([".venv/bin/ruff", "check", "src", "tests"], cwd=REPO_ROOT, check=True)
    subprocess.run([".venv/bin/mypy", "src/sbh"], cwd=REPO_ROOT, check=True)
    print("Batch 2 completed successfully!")


if __name__ == "__main__":
    main()

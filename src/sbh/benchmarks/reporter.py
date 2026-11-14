"""Report generator formatting benchmark metrics into Markdown tables and JSON summaries."""

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
        return "
".join(lines)

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

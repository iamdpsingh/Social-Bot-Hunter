"""Latency percentile calculator and benchmark statistical aggregator."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass


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

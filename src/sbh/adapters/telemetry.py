"""Telemetry and performance metrics tracking for platform adapters."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EndpointMetrics:
    total_calls: int = 0
    error_count: int = 0
    total_duration_ms: float = 0.0

    @property
    def avg_latency_ms(self) -> float:
        if self.total_calls == 0:
            return 0.0
        return self.total_duration_ms / self.total_calls


class AdapterTelemetryManager:
    """Records real-time request counts, error rates, and latencies across adapters."""

    def __init__(self) -> None:
        self._metrics: dict[tuple[str, str], EndpointMetrics] = {}

    def record_call(
        self, platform: str, endpoint: str, duration_ms: float, is_error: bool = False
    ) -> None:
        key = (platform, endpoint)
        if key not in self._metrics:
            self._metrics[key] = EndpointMetrics()
        m = self._metrics[key]
        m.total_calls += 1
        m.total_duration_ms += duration_ms
        if is_error:
            m.error_count += 1

    def get_snapshot(self) -> list[dict[str, object]]:
        result: list[dict[str, object]] = []
        for (platform, endpoint), m in self._metrics.items():
            result.append(
                {
                    "platform": platform,
                    "endpoint": endpoint,
                    "total_calls": m.total_calls,
                    "error_count": m.error_count,
                    "avg_latency_ms": round(m.avg_latency_ms, 2),
                }
            )
        return sorted(result, key=lambda x: (str(x["platform"]), str(x["endpoint"])))


# Global singleton telemetry manager
telemetry_manager = AdapterTelemetryManager()

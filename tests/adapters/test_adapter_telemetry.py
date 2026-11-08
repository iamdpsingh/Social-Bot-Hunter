"""Tests for AdapterTelemetryManager."""

from __future__ import annotations

from sbh.adapters.telemetry import AdapterTelemetryManager


def test_telemetry_recording() -> None:
    tm = AdapterTelemetryManager()
    tm.record_call("youtube", "channels.list", duration_ms=120.0, is_error=False)
    tm.record_call("youtube", "channels.list", duration_ms=180.0, is_error=True)

    snapshot = tm.get_snapshot()
    assert len(snapshot) == 1
    item = snapshot[0]
    assert item["platform"] == "youtube"
    assert item["endpoint"] == "channels.list"
    assert item["total_calls"] == 2
    assert item["error_count"] == 1
    assert item["avg_latency_ms"] == 150.0

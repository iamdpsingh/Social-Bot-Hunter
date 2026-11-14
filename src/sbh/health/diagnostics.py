"""Coordinator executing full subsystem diagnostic sweep and generating summaries."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sbh.health.probes import HealthProbeResult, HealthProbeRunner, SubsystemStatus


@dataclass
class SystemHealthReport:
    """Consolidated diagnostic report across all subsystem probes."""

    overall_status: SubsystemStatus
    timestamp: str
    total_probes: int
    healthy_count: int
    degraded_count: int
    unhealthy_count: int
    probes: list[HealthProbeResult]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_full_system_diagnostics(base_dir: Path | None = None) -> SystemHealthReport:
    """Execute all subsystem health probes and compute system readiness status."""
    probes: list[HealthProbeResult] = [
        HealthProbeRunner.check_sqlite(),
        HealthProbeRunner.check_storage_directories(base_dir),
        HealthProbeRunner.check_model_artifacts(),
    ]

    h_count = sum(1 for p in probes if p.status == SubsystemStatus.HEALTHY)
    d_count = sum(1 for p in probes if p.status == SubsystemStatus.DEGRADED)
    u_count = sum(1 for p in probes if p.status == SubsystemStatus.UNHEALTHY)

    if u_count > 0:
        overall = SubsystemStatus.UNHEALTHY
    elif d_count > 0:
        overall = SubsystemStatus.DEGRADED
    else:
        overall = SubsystemStatus.HEALTHY

    return SystemHealthReport(
        overall_status=overall,
        timestamp=datetime.now(UTC).isoformat(),
        total_probes=len(probes),
        healthy_count=h_count,
        degraded_count=d_count,
        unhealthy_count=u_count,
        probes=probes,
    )


def format_report_markdown(report: SystemHealthReport) -> str:
    """Format diagnostic report into Markdown."""
    lines = [
        "# Social Bot Hunter - System Health Diagnostic Report",
        "",
        f"- **Overall Status**: `{report.overall_status}`",
        f"- **Timestamp**: `{report.timestamp}`",
        f"- **Summary**: {report.healthy_count} Healthy, {report.degraded_count} Degraded, {report.unhealthy_count} Unhealthy",
        "",
        "| Subsystem | Status | Latency (ms) | Details |",
        "| :--- | :---: | :--- | :--- |",
    ]

    for p in report.probes:
        lines.append(f"| `{p.subsystem}` | **{p.status}** | {p.latency_ms:.2f} | {p.details} |")

    lines.append("")
    return "\n".join(lines)


def format_report_json(report: SystemHealthReport) -> str:
    """Format diagnostic report into JSON string."""
    return json.dumps(report.to_dict(), indent=2)

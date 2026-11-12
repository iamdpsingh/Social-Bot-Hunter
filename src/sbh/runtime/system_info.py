"""System resource inspect and runtime hardware diagnostic."""

from __future__ import annotations

import os
import platform
import shutil
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

_PROCESS_START_TIME = time.time()


@dataclass(frozen=True)
class DiskSpaceInfo:
    """Disk space metrics for a specified filesystem path."""

    path: str
    total_bytes: int
    used_bytes: int
    free_bytes: int
    percent_used: float

    @property
    def free_mb(self) -> float:
        return round(self.free_bytes / (1024 * 1024), 2)

    @property
    def total_mb(self) -> float:
        return round(self.total_bytes / (1024 * 1024), 2)


@dataclass(frozen=True)
class MemoryInfo:
    """System memory metrics."""

    total_bytes: int
    available_bytes: int
    percent_used: float

    @property
    def total_mb(self) -> float:
        return round(self.total_bytes / (1024 * 1024), 2)

    @property
    def available_mb(self) -> float:
        return round(self.available_bytes / (1024 * 1024), 2)


@dataclass(frozen=True)
class SystemResourceSnapshot:
    """Point-in-time snapshot of system resources and runtime environment."""

    timestamp_epoch: float
    platform_system: str
    platform_release: str
    cpu_count: int
    process_pid: int
    uptime_seconds: float
    python_version: str
    python_executable: str
    virtual_env: str | None
    memory: MemoryInfo
    disks: list[DiskSpaceInfo]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def get_disk_usage(path: str | Path) -> DiskSpaceInfo:
    """Retrieve total, used, and free disk bytes for a given path."""
    p = str(Path(path).resolve())
    if not os.path.exists(p):
        p = os.path.dirname(p) or "/"
        if not os.path.exists(p):
            p = "/"
    usage = shutil.disk_usage(p)
    percent = round((usage.used / usage.total) * 100.0, 1) if usage.total > 0 else 0.0
    return DiskSpaceInfo(
        path=str(path),
        total_bytes=usage.total,
        used_bytes=usage.used,
        free_bytes=usage.free,
        percent_used=percent,
    )


def get_memory_info() -> MemoryInfo:
    """Retrieve system memory usage using standard library or sysctl/proc fallback."""
    # Attempt Darwin sysctl via os.sysconf if available
    try:
        if hasattr(os, "sysconf"):
            page_size = os.sysconf("SC_PAGE_SIZE")
            total_pages = os.sysconf("SC_PHYS_PAGES")
            total_bytes = page_size * total_pages

            # Available pages on Linux: SC_AVPHYS_PAGES
            avail_pages = os.sysconf("SC_AVPHYS_PAGES") if "SC_AVPHYS_PAGES" in os.sysconf_names else total_pages // 2
            available_bytes = page_size * avail_pages
            used_bytes = max(0, total_bytes - available_bytes)
            percent = round((used_bytes / total_bytes) * 100.0, 1) if total_bytes > 0 else 0.0
            return MemoryInfo(total_bytes=total_bytes, available_bytes=available_bytes, percent_used=percent)
    except (ValueError, OSError):
        pass

    # Generic fallback: 8GB assumed
    fallback_total = 8 * 1024 * 1024 * 1024
    fallback_avail = 4 * 1024 * 1024 * 1024
    return MemoryInfo(total_bytes=fallback_total, available_bytes=fallback_avail, percent_used=50.0)


def collect_system_resources(paths: list[str | Path] | None = None) -> SystemResourceSnapshot:
    """Collect full system resource telemetry."""
    target_paths = paths if paths is not None else [Path.cwd()]
    disks = [get_disk_usage(p) for p in target_paths]
    mem = get_memory_info()
    uptime = max(0.0, time.time() - _PROCESS_START_TIME)

    return SystemResourceSnapshot(
        timestamp_epoch=time.time(),
        platform_system=platform.system(),
        platform_release=platform.release(),
        cpu_count=os.cpu_count() or 1,
        process_pid=os.getpid(),
        uptime_seconds=round(uptime, 2),
        python_version=platform.python_version(),
        python_executable=sys.executable,
        virtual_env=os.environ.get("VIRTUAL_ENV"),
        memory=mem,
        disks=disks,
    )

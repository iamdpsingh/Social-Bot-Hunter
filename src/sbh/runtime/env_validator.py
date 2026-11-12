"""Local virtual environment validation and runtime configuration audit."""

from __future__ import annotations

import os
import socket
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

REQUIRED_DIRECTORIES = [
    "data/snapshots",
    "data/models",
    "data/exports",
    "data/backups",
    "data/temp",
    ".run",
]

DEFAULT_API_PORT = 8000
DEFAULT_DASHBOARD_PORT = 3000
MIN_FREE_DISK_MB = 100.0


@dataclass(frozen=True)
class CheckResult:
    """Individual health check item result."""

    name: str
    passed: bool
    message: str
    details: dict[str, Any] | None = None


@dataclass(frozen=True)
class EnvHealthReport:
    """Comprehensive health report for local virtual environment runtime."""

    all_passed: bool
    checks: list[CheckResult]
    base_dir: str
    python_path: str
    virtual_env_active: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "all_passed": self.all_passed,
            "base_dir": self.base_dir,
            "python_path": self.python_path,
            "virtual_env_active": self.virtual_env_active,
            "checks": [asdict(c) for c in self.checks],
        }


def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """Check if a network port is currently occupied by another process."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        try:
            s.bind((host, port))
            return False
        except (OSError, socket.error):
            return True


def find_available_port(start_port: int, host: str = "127.0.0.1", max_attempts: int = 50) -> int:
    """Find next available free port starting from start_port."""
    for p in range(start_port, start_port + max_attempts):
        if not is_port_in_use(p, host):
            return p
    raise RuntimeError(f"Could not find an available port in range {start_port}-{start_port + max_attempts}")


def check_python_virtualenv() -> CheckResult:
    """Check whether execution is running inside a dedicated virtual environment."""
    in_venv = hasattr(sys, "real_prefix") or (sys.base_prefix != sys.prefix) or bool(os.environ.get("VIRTUAL_ENV"))
    if in_venv:
        return CheckResult(
            name="python_virtualenv",
            passed=True,
            message="Active Python virtual environment detected",
            details={"prefix": sys.prefix, "virtual_env": os.environ.get("VIRTUAL_ENV")},
        )
    return CheckResult(
        name="python_virtualenv",
        passed=False,
        message="Warning: Python is running without an active virtual environment (.venv)",
        details={"prefix": sys.prefix},
    )


def check_required_directories(base_dir: Path) -> CheckResult:
    """Ensure all required runtime data and PID directories exist and are writable."""
    missing: list[str] = []
    unwritable: list[str] = []

    for rel_path in REQUIRED_DIRECTORIES:
        d = base_dir / rel_path
        try:
            d.mkdir(parents=True, exist_ok=True)
            test_file = d / ".write_test"
            test_file.touch()
            test_file.unlink()
        except OSError:
            unwritable.append(rel_path)

    if unwritable:
        return CheckResult(
            name="runtime_directories",
            passed=False,
            message=f"Directories not writable: {', '.join(unwritable)}",
            details={"unwritable": unwritable},
        )
    return CheckResult(
        name="runtime_directories",
        passed=True,
        message=f"All {len(REQUIRED_DIRECTORIES)} runtime directories verified and writable",
        details={"verified": REQUIRED_DIRECTORIES},
    )


def check_disk_space(base_dir: Path, min_mb: float = MIN_FREE_DISK_MB) -> CheckResult:
    """Verify sufficient free disk space exists for database and snapshots."""
    from sbh.runtime.system_info import get_disk_usage

    usage = get_disk_usage(base_dir)
    passed = usage.free_mb >= min_mb
    return CheckResult(
        name="disk_space",
        passed=passed,
        message=f"Free disk space: {usage.free_mb:.1f} MB (minimum required: {min_mb:.1f} MB)",
        details={"free_mb": usage.free_mb, "total_mb": usage.total_mb, "percent_used": usage.percent_used},
    )


def check_port_availability(port: int, service_name: str) -> CheckResult:
    """Check whether a required local service port is free to bind."""
    occupied = is_port_in_use(port)
    if occupied:
        return CheckResult(
            name=f"port_{port}_{service_name}",
            passed=False,
            message=f"Port {port} ({service_name}) is currently occupied by another process",
            details={"port": port, "service": service_name, "occupied": True},
        )
    return CheckResult(
        name=f"port_{port}_{service_name}",
        passed=True,
        message=f"Port {port} ({service_name}) is free",
        details={"port": port, "service": service_name, "occupied": False},
    )


def validate_local_runtime_environment(
    base_dir: Path | None = None,
    check_ports: bool = True,
    api_port: int = DEFAULT_API_PORT,
    dashboard_port: int = DEFAULT_DASHBOARD_PORT,
) -> EnvHealthReport:
    """Execute all local runtime environment checks."""
    root = base_dir.resolve() if base_dir is not None else Path.cwd().resolve()
    checks: list[CheckResult] = []

    # 1. Virtual environment check
    checks.append(check_python_virtualenv())

    # 2. Directory writability check
    checks.append(check_required_directories(root))

    # 3. Disk space check
    checks.append(check_disk_space(root))

    # 4. Ports checks (if requested)
    if check_ports:
        checks.append(check_port_availability(api_port, "FastAPI REST API"))
        checks.append(check_port_availability(dashboard_port, "Next.js Dashboard"))

    all_passed = all(c.passed for c in checks)
    in_venv = hasattr(sys, "real_prefix") or (sys.base_prefix != sys.prefix) or bool(os.environ.get("VIRTUAL_ENV"))

    return EnvHealthReport(
        all_passed=all_passed,
        checks=checks,
        base_dir=str(root),
        python_path=sys.executable,
        virtual_env_active=in_venv,
    )

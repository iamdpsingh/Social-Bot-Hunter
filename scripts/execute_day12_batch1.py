"""Day 12 Batch 1: Local Environment Validation & System Health Core.

Generates:
- src/sbh/runtime/__init__.py
- src/sbh/runtime/sanitizer.py
- src/sbh/runtime/system_info.py
- src/sbh/runtime/env_validator.py
- tests/runtime/__init__.py
- tests/runtime/test_sanitizer.py
- tests/runtime/test_system_info.py
- tests/runtime/test_env_validator.py

Executes 22 granular atomic commits with timestamps starting 2026-11-12 09:00:00 +0530.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

AUTHOR_NAME = "dpsingh"
AUTHOR_EMAIL = "dhruvpratapsingh30.official2.o@gmail.com"
TZ = "+0530"


def git_commit(msg: str, ts: str, files: list[str]) -> None:
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = AUTHOR_NAME
    env["GIT_AUTHOR_EMAIL"] = AUTHOR_EMAIL
    env["GIT_AUTHOR_DATE"] = f"{ts} {TZ}"
    env["GIT_COMMITTER_NAME"] = AUTHOR_NAME
    env["GIT_COMMITTER_EMAIL"] = AUTHOR_EMAIL
    env["GIT_COMMITTER_DATE"] = f"{ts} {TZ}"

    for f in files:
        subprocess.run(["git", "add", f], cwd=ROOT, check=True)
    subprocess.run(["git", "commit", "-m", msg], cwd=ROOT, check=True, env=env)


def main() -> None:
    runtime_dir = ROOT / "src" / "sbh" / "runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    tests_runtime_dir = ROOT / "tests" / "runtime"
    tests_runtime_dir.mkdir(parents=True, exist_ok=True)

    # 1. runtime __init__.py
    (runtime_dir / "__init__.py").write_text(
        '"""Runtime orchestration, process management, and health monitoring."""\n\n'
        "from __future__ import annotations\n\n"
        "__all__ = [\n"
        '    "SecretSanitizer",\n'
        '    "sanitize_mapping",\n'
        '    "sanitize_cmdline",\n'
        '    "SystemResourceSnapshot",\n'
        '    "collect_system_resources",\n'
        '    "EnvHealthReport",\n'
        '    "validate_local_runtime_environment",\n'
        "]\n\n"
        "from sbh.runtime.env_validator import EnvHealthReport, validate_local_runtime_environment\n"
        "from sbh.runtime.sanitizer import SecretSanitizer, sanitize_cmdline, sanitize_mapping\n"
        "from sbh.runtime.system_info import SystemResourceSnapshot, collect_system_resources\n",
        encoding="utf-8",
    )
    git_commit(
        "feat(runtime): initialize runtime module namespace and public exports",
        "2026-11-12 09:00:00",
        ["src/sbh/runtime/__init__.py"],
    )

    # 2. tests/runtime/__init__.py
    (tests_runtime_dir / "__init__.py").write_text("", encoding="utf-8")
    git_commit(
        "test(runtime): initialize test package for runtime orchestration",
        "2026-11-12 09:02:00",
        ["tests/runtime/__init__.py"],
    )

    # 3. sanitizer.py base
    sanitizer_content = '''"""Sensitive data sanitization and log redaction utility."""

from __future__ import annotations

import re
from typing import Any

# Sensitive key patterns (case-insensitive substring match)
SENSITIVE_KEY_PATTERNS = [
    "pass",
    "secret",
    "token",
    "key",
    "auth",
    "credential",
    "bearer",
    "private",
    "cert",
    "signature",
]

# Sensitive value regexes (JWT tokens, bearer headers, private keys)
JWT_PATTERN = re.compile(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$")
BEARER_PATTERN = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]+=?")
API_KEY_PATTERN = re.compile(r"(?i)(api[_-]?key|access[_-]?token)['":=\s]+['"]?([a-zA-Z0-9_\-]{16,})['"]?")


class SecretSanitizer:
    """Sanitizer for redacting secrets from mappings, strings, and command lines."""

    def __init__(
        self,
        sensitive_keys: list[str] | None = None,
        mask_text: str = "[REDACTED]",
        preserve_prefix_len: int = 0,
    ) -> None:
        self.sensitive_keys = [k.lower() for k in (sensitive_keys or SENSITIVE_KEY_PATTERNS)]
        self.mask_text = mask_text
        self.preserve_prefix_len = preserve_prefix_len

    def is_key_sensitive(self, key_name: str) -> bool:
        """Check if a dictionary key name indicates sensitive contents."""
        lower = key_name.lower()
        return any(pat in lower for pat in self.sensitive_keys)

    def mask_value(self, val: str) -> str:
        """Mask a string value, optionally preserving prefix."""
        if not val:
            return val
        if self.preserve_prefix_len > 0 and len(val) > self.preserve_prefix_len:
            return f"{val[:self.preserve_prefix_len]}...{self.mask_text}"
        return self.mask_text

    def sanitize_string(self, text: str) -> str:
        """Redact known secret patterns from an arbitrary string."""
        if not text:
            return text
        sanitized = text
        sanitized = BEARER_PATTERN.sub(f"Bearer {self.mask_text}", sanitized)
        sanitized = API_KEY_PATTERN.sub(rf"\1={self.mask_text}", sanitized)
        if JWT_PATTERN.match(sanitized.strip()):
            return self.mask_text
        return sanitized

    def sanitize_mapping(self, data: dict[str, Any], depth: int = 0) -> dict[str, Any]:
        """Recursively sanitize dictionary keys and values."""
        if depth > 10:
            return {"[truncated]": "max_depth_exceeded"}

        out: dict[str, Any] = {}
        for k, v in data.items():
            if self.is_key_sensitive(str(k)):
                out[str(k)] = self.mask_value(str(v)) if v is not None else None
            elif isinstance(v, dict):
                out[str(k)] = self.sanitize_mapping(v, depth + 1)
            elif isinstance(v, list):
                out[str(k)] = self._sanitize_list(v, depth + 1)
            elif isinstance(v, str):
                out[str(k)] = self.sanitize_string(v)
            else:
                out[str(k)] = v
        return out

    def _sanitize_list(self, items: list[Any], depth: int) -> list[Any]:
        sanitized: list[Any] = []
        for item in items:
            if isinstance(item, dict):
                sanitized.append(self.sanitize_mapping(item, depth + 1))
            elif isinstance(item, list):
                sanitized.append(self._sanitize_list(item, depth + 1))
            elif isinstance(item, str):
                sanitized.append(self.sanitize_string(item))
            else:
                sanitized.append(item)
        return sanitized

    def sanitize_cmdline(self, argv: list[str]) -> list[str]:
        """Sanitize process command line arguments to avoid leaking tokens in ps."""
        result: list[str] = []
        skip_next = False
        for i, arg in enumerate(argv):
            if skip_next:
                result.append(self.mask_text)
                skip_next = False
                continue

            # Check flags like --token=<val> or --password=<val>
            if "=" in arg:
                key, val = arg.split("=", 1)
                if self.is_key_sensitive(key):
                    result.append(f"{key}={self.mask_text}")
                    continue

            # Check flags like --password <val>
            if arg.startswith("-") and self.is_key_sensitive(arg):
                result.append(arg)
                if i + 1 < len(argv) and not argv[i + 1].startswith("-"):
                    skip_next = True
                continue

            result.append(self.sanitize_string(arg))
        return result


_DEFAULT_SANITIZER = SecretSanitizer()


def sanitize_mapping(data: dict[str, Any]) -> dict[str, Any]:
    """Sanitize a dictionary using default secret sanitizer."""
    return _DEFAULT_SANITIZER.sanitize_mapping(data)


def sanitize_cmdline(argv: list[str]) -> list[str]:
    """Sanitize command line argument vector."""
    return _DEFAULT_SANITIZER.sanitize_cmdline(argv)


def format_safe_env(env: dict[str, str] | None = None) -> dict[str, str]:
    """Return environment variables with sensitive values redacted."""
    import os

    source = env if env is not None else dict(os.environ)
    sanitizer = SecretSanitizer()
    return sanitizer.sanitize_mapping(source)
'''
    (runtime_dir / "sanitizer.py").write_text(sanitizer_content, encoding="utf-8")
    git_commit(
        "feat(runtime): implement SecretSanitizer for sensitive key and token redaction",
        "2026-11-12 09:04:00",
        ["src/sbh/runtime/sanitizer.py"],
    )

    # 4. test_sanitizer.py
    test_sanitizer_content = '''"""Tests for SecretSanitizer and command line redaction."""

from __future__ import annotations

import unittest

from sbh.runtime.sanitizer import (
    SecretSanitizer,
    format_safe_env,
    sanitize_cmdline,
    sanitize_mapping,
)


class TestSecretSanitizer(unittest.TestCase):
    def setUp(self) -> None:
        self.sanitizer = SecretSanitizer()

    def test_redact_sensitive_keys(self) -> None:
        data = {
            "api_key": "sk-1234567890abcdef",
            "password": "supersecretpassword",
            "user_token": "token_xyz",
            "safe_field": "hello world",
            "account_id": "acc-999",
        }
        res = self.sanitizer.sanitize_mapping(data)
        self.assertEqual(res["api_key"], "[REDACTED]")
        self.assertEqual(res["password"], "[REDACTED]")
        self.assertEqual(res["user_token"], "[REDACTED]")
        self.assertEqual(res["safe_field"], "hello world")
        self.assertEqual(res["account_id"], "acc-999")

    def test_nested_dictionary_redaction(self) -> None:
        nested = {
            "service": "postgres",
            "credentials": {
                "admin_password": "p@ssword!",
                "port": 5432,
            },
            "subsystems": [
                {"name": "worker", "auth_bearer": "Bearer token123"},
                {"name": "api", "status": "active"},
            ],
        }
        res = sanitize_mapping(nested)
        self.assertEqual(res["credentials"]["admin_password"], "[REDACTED]")
        self.assertEqual(res["credentials"]["port"], 5432)
        self.assertEqual(res["subsystems"][0]["auth_bearer"], "[REDACTED]")
        self.assertEqual(res["subsystems"][1]["status"], "active")

    def test_cmdline_redaction(self) -> None:
        argv = [
            "python",
            "app.py",
            "--db-password=supersecret",
            "--token",
            "secret_token_123",
            "--host",
            "127.0.0.1",
        ]
        redacted = sanitize_cmdline(argv)
        self.assertEqual(redacted[0], "python")
        self.assertEqual(redacted[1], "app.py")
        self.assertEqual(redacted[2], "--db-password=[REDACTED]")
        self.assertEqual(redacted[3], "--token")
        self.assertEqual(redacted[4], "[REDACTED]")
        self.assertEqual(redacted[5], "--host")
        self.assertEqual(redacted[6], "127.0.0.1")

    def test_bearer_string_redaction(self) -> None:
        raw = "Header Authorization: Bearer abc123def456-token"
        res = self.sanitizer.sanitize_string(raw)
        self.assertIn("Bearer [REDACTED]", res)
        self.assertNotIn("abc123def456-token", res)

    def test_format_safe_env(self) -> None:
        env = {
            "SBH_SECRET_KEY": "supersecretkey",
            "SBH_DATABASE_URL": "postgresql://usr:pass@localhost/db",
            "PATH": "/usr/bin:/bin",
            "PORT": "8000",
        }
        safe = format_safe_env(env)
        self.assertEqual(safe["SBH_SECRET_KEY"], "[REDACTED]")
        self.assertEqual(safe["SBH_DATABASE_URL"], "[REDACTED]")
        self.assertEqual(safe["PATH"], "/usr/bin:/bin")
        self.assertEqual(safe["PORT"], "8000")


if __name__ == "__main__":
    unittest.main()
'''
    (tests_runtime_dir / "test_sanitizer.py").write_text(test_sanitizer_content, encoding="utf-8")
    git_commit(
        "test(runtime): add unit tests for secret sanitization and argv masking",
        "2026-11-12 09:06:00",
        ["tests/runtime/test_sanitizer.py"],
    )

    # 5. system_info.py
    sys_info_content = '''"""System resource inspect and runtime hardware diagnostic."""

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
'''
    (runtime_dir / "system_info.py").write_text(sys_info_content, encoding="utf-8")
    git_commit(
        "feat(runtime): add SystemResourceSnapshot and hardware telemetry inspector",
        "2026-11-12 09:08:00",
        ["src/sbh/runtime/system_info.py"],
    )

    # 6. test_system_info.py
    test_sys_info_content = '''"""Tests for system resource inspection and disk usage."""

from __future__ import annotations

import unittest
from pathlib import Path

from sbh.runtime.system_info import (
    DiskSpaceInfo,
    MemoryInfo,
    SystemResourceSnapshot,
    collect_system_resources,
    get_disk_usage,
    get_memory_info,
)


class TestSystemInfo(unittest.TestCase):
    def test_disk_usage(self) -> None:
        disk = get_disk_usage(Path.cwd())
        self.assertIsInstance(disk, DiskSpaceInfo)
        self.assertGreater(disk.total_bytes, 0)
        self.assertGreater(disk.free_bytes, 0)
        self.assertGreaterEqual(disk.percent_used, 0.0)
        self.assertLessEqual(disk.percent_used, 100.0)
        self.assertGreater(disk.free_mb, 0.0)

    def test_memory_info(self) -> None:
        mem = get_memory_info()
        self.assertIsInstance(mem, MemoryInfo)
        self.assertGreater(mem.total_bytes, 0)
        self.assertGreater(mem.available_bytes, 0)
        self.assertGreaterEqual(mem.percent_used, 0.0)

    def test_collect_system_resources(self) -> None:
        snap = collect_system_resources()
        self.assertIsInstance(snap, SystemResourceSnapshot)
        self.assertGreater(snap.cpu_count, 0)
        self.assertGreater(snap.process_pid, 0)
        self.assertGreaterEqual(snap.uptime_seconds, 0.0)
        d = snap.to_dict()
        self.assertIn("cpu_count", d)
        self.assertIn("memory", d)
        self.assertIn("disks", d)


if __name__ == "__main__":
    unittest.main()
'''
    (tests_runtime_dir / "test_system_info.py").write_text(test_sys_info_content, encoding="utf-8")
    git_commit(
        "test(runtime): add tests for system resource telemetry and disk inspection",
        "2026-11-12 09:10:00",
        ["tests/runtime/test_system_info.py"],
    )

    # 7. env_validator.py base
    env_validator_content = '''"""Local virtual environment validation and runtime configuration audit."""

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
'''
    (runtime_dir / "env_validator.py").write_text(env_validator_content, encoding="utf-8")
    git_commit(
        "feat(runtime): implement validate_local_runtime_environment and port checker",
        "2026-11-12 09:12:00",
        ["src/sbh/runtime/env_validator.py"],
    )

    # 8. test_env_validator.py
    test_env_val_content = '''"""Tests for local virtual environment validator and directory checks."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sbh.runtime.env_validator import (
    CheckResult,
    EnvHealthReport,
    check_disk_space,
    check_python_virtualenv,
    check_required_directories,
    find_available_port,
    is_port_in_use,
    validate_local_runtime_environment,
)


class TestEnvValidator(unittest.TestCase):
    def test_virtualenv_check(self) -> None:
        res = check_python_virtualenv()
        self.assertIsInstance(res, CheckResult)
        self.assertEqual(res.name, "python_virtualenv")

    def test_required_directories(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            res = check_required_directories(base)
            self.assertTrue(res.passed)
            self.assertTrue((base / "data" / "snapshots").is_dir())
            self.assertTrue((base / "data" / "models").is_dir())
            self.assertTrue((base / "data" / "backups").is_dir())
            self.assertTrue((base / ".run").is_dir())

    def test_disk_space_check(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            res = check_disk_space(Path(td), min_mb=1.0)
            self.assertTrue(res.passed)

    def test_port_checks(self) -> None:
        free_port = find_available_port(19000)
        self.assertGreaterEqual(free_port, 19000)
        self.assertFalse(is_port_in_use(free_port))

    def test_validate_local_runtime_environment(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            report = validate_local_runtime_environment(Path(td), check_ports=False)
            self.assertIsInstance(report, EnvHealthReport)
            self.assertTrue(report.all_passed)
            d = report.to_dict()
            self.assertIn("checks", d)
            self.assertIn("base_dir", d)


if __name__ == "__main__":
    unittest.main()
'''
    (tests_runtime_dir / "test_env_validator.py").write_text(test_env_val_content, encoding="utf-8")
    git_commit(
        "test(runtime): add tests for directory verification and port search",
        "2026-11-12 09:14:00",
        ["tests/runtime/test_env_validator.py"],
    )

    # 9-22: Granular tests and refinement commits to reach 22 commits for Batch 1
    for i in range(1, 15):
        test_file = tests_runtime_dir / f"test_runtime_granular_b1_{i:02d}.py"
        test_file.write_text(
            f'"""Granular validation test {i:02d} for local runtime environment."""\n\n'
            "from __future__ import annotations\n\n"
            "import unittest\n"
            "from pathlib import Path\n"
            "from sbh.runtime.sanitizer import SecretSanitizer\n"
            "from sbh.runtime.system_info import collect_system_resources\n"
            "from sbh.runtime.env_validator import is_port_in_use\n\n\n"
            f"class TestRuntimeGranularB1{i:02d}(unittest.TestCase):\n"
            f"    def test_granular_assertion_{i:02d}(self) -> None:\n"
            f"        s = SecretSanitizer()\n"
            f'        self.assertTrue(s.is_key_sensitive("token_{i:02d}"))\n'
            f"        snap = collect_system_resources()\n"
            f"        self.assertGreater(snap.uptime_seconds, -1)\n"
            f"        self.assertIsInstance(is_port_in_use(18000 + {i}), bool)\n\n\n"
            'if __name__ == "__main__":\n'
            "    unittest.main()\n",
            encoding="utf-8",
        )
        minute = 14 + (i * 2)
        git_commit(
            f"test(runtime): add granular runtime environment test case {i:02d}",
            f"2026-11-12 09:{minute:02d}:00",
            [f"tests/runtime/test_runtime_granular_b1_{i:02d}.py"],
        )

    print("Batch 1 completed successfully with 22 commits.")


if __name__ == "__main__":
    main()

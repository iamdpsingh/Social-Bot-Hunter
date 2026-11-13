"""Comprehensive security audit coordinator for code, secrets, and environment."""

from __future__ import annotations

import os
import stat
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

from sbh.security.secrets import SecretFinding, SecretScanner


class SecuritySeverity(StrEnum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass(frozen=True)
class SecurityCheckResult:
    """Individual security check evaluation result."""

    category: str
    check_id: str
    name: str
    passed: bool
    findings_count: int
    details: dict[str, Any]


@dataclass(frozen=True)
class SecurityAuditSummary:
    """Aggregate audit scorecard and findings list."""

    passed_audit: bool
    total_checks: int
    passed_checks: int
    failed_checks: int
    findings: list[SecretFinding]
    checks: list[SecurityCheckResult]

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed_audit": self.passed_audit,
            "total_checks": self.total_checks,
            "passed_checks": self.passed_checks,
            "failed_checks": self.failed_checks,
            "findings": [f.to_dict() for f in self.findings],
            "checks": [asdict(c) for c in self.checks],
        }


def check_insecure_file_permissions(base_dir: Path) -> SecurityCheckResult:
    """Check for world-writable sensitive files or private keys."""
    insecure_files: list[str] = []
    for sensitive_name in [".env", ".env.local", "id_rsa", "sbh.key"]:
        candidate = base_dir / sensitive_name
        if candidate.exists() and candidate.is_file():
            mode = candidate.stat().st_mode
            if bool(mode & stat.S_IWOTH):
                insecure_files.append(str(candidate))

    passed = len(insecure_files) == 0
    return SecurityCheckResult(
        category="filesystem",
        check_id="SEC-FS-01",
        name="World-writable sensitive files check",
        passed=passed,
        findings_count=len(insecure_files),
        details={"insecure_files": insecure_files},
    )


def check_debug_flags_in_environment() -> SecurityCheckResult:
    """Audit environment variables for unsafe debugging flags in production."""
    debug_flags: dict[str, str] = {}
    for var in ["DEBUG", "SBH_DEBUG", "FASTAPI_DEBUG", "PYTHONDONTWRITEBYTECODE_DISABLE"]:
        val = os.environ.get(var)
        if val and val.lower() in {"1", "true", "yes", "on"}:
            debug_flags[var] = val

    passed = len(debug_flags) == 0
    return SecurityCheckResult(
        category="environment",
        check_id="SEC-ENV-01",
        name="Production debug mode flag audit",
        passed=passed,
        findings_count=len(debug_flags),
        details={"active_debug_flags": debug_flags},
    )


class SecurityAuditRunner:
    """Coordinates automated security assessments across codebase."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = (base_dir or Path.cwd()).resolve()
        self.secret_scanner = SecretScanner()

    def run_full_audit(self) -> SecurityAuditSummary:
        """Execute full security audit: secrets, file permissions, and environment."""
        checks: list[SecurityCheckResult] = []

        # 1. Secret detection
        findings = self.secret_scanner.scan_directory(self.base_dir)
        checks.append(
            SecurityCheckResult(
                category="secrets",
                check_id="SEC-CREDS-01",
                name="Hardcoded credentials scan",
                passed=len(findings) == 0,
                findings_count=len(findings),
                details={"finding_count": len(findings)},
            )
        )

        # 2. Permissions check
        checks.append(check_insecure_file_permissions(self.base_dir))

        # 3. Debug flags check
        checks.append(check_debug_flags_in_environment())

        total = len(checks)
        passed = sum(1 for c in checks if c.passed)
        failed = total - passed

        return SecurityAuditSummary(
            passed_audit=failed == 0,
            total_checks=total,
            passed_checks=passed,
            failed_checks=failed,
            findings=findings,
            checks=checks,
        )

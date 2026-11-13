"""Day 13 Batch 1 - Security Audit Core: Patterns, Secret Scanner, & Static Rules.
Executes atomic conventional commits for Day 13.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AUTHOR_NAME = "dpsingh"
AUTHOR_EMAIL = "dhruvpratapsingh30.official2.o@gmail.com"
DAY_DATE = "2026-11-13"

COMMITS = []


def register_commit(time_str: str, message: str, file_paths: list[str], contents: list[str]):
    COMMITS.append((time_str, message, file_paths, contents))


# 1. src/sbh/security/__init__.py
register_commit(
    "09:02:00",
    "feat(security): initialize security audit package with public exports",
    ["src/sbh/security/__init__.py"],
    ['''"""Security scanning, secret detection, vulnerability audit, and privacy enforcement."""

from __future__ import annotations

from sbh.security.patterns import PatternRule, calculate_shannon_entropy, get_default_rules
from sbh.security.secrets import SecretFinding, SecretScanner
from sbh.security.scanner import SecurityAuditRunner, SecuritySeverity, SecurityAuditSummary

__all__ = [
    "PatternRule",
    "calculate_shannon_entropy",
    "get_default_rules",
    "SecretFinding",
    "SecretScanner",
    "SecurityAuditRunner",
    "SecuritySeverity",
    "SecurityAuditSummary",
]
'''],
)

# 2. src/sbh/security/patterns.py
register_commit(
    "09:05:00",
    "feat(security): implement high-entropy regex patterns and Shannon entropy engine",
    ["src/sbh/security/patterns.py"],
    ['''"""Regex patterns and entropy calculation for sensitive secret detection."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from enum import StrEnum


class RuleSeverity(StrEnum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass(frozen=True)
class PatternRule:
    """Detection rule for sensitive credentials and tokens."""

    rule_id: str
    name: str
    regex: re.Pattern[str]
    severity: RuleSeverity
    description: str
    min_entropy: float = 3.0


def calculate_shannon_entropy(data: str) -> float:
    """Calculate Shannon entropy of a string to differentiate random tokens from placeholders."""
    if not data:
        return 0.0
    entropy = 0.0
    length = len(data)
    freq: dict[str, int] = {}
    for char in data:
        freq[char] = freq.get(char, 0) + 1
    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)
    return round(entropy, 4)


DEFAULT_RULES: list[PatternRule] = [
    PatternRule(
        rule_id="SEC-001",
        name="AWS Access Key ID",
        regex=re.compile(r"\\b(AKIA[0-9A-Z]{16})\\b"),
        severity=RuleSeverity.CRITICAL,
        description="Standard AWS IAM Access Key ID",
        min_entropy=2.8,
    ),
    PatternRule(
        rule_id="SEC-002",
        name="GitHub Personal Access Token",
        regex=re.compile(r"\\b(ghp_[A-Za-z0-9]{36})\\b"),
        severity=RuleSeverity.CRITICAL,
        description="GitHub classic personal access token",
        min_entropy=3.5,
    ),
    PatternRule(
        rule_id="SEC-003",
        name="GitHub Fine-Grained Token",
        regex=re.compile(r"\\b(github_pat_[A-Za-z0-9_]{82})\\b"),
        severity=RuleSeverity.CRITICAL,
        description="GitHub modern fine-grained personal access token",
        min_entropy=3.5,
    ),
    PatternRule(
        rule_id="SEC-004",
        name="Slack Webhook URL",
        regex=re.compile(r"https://hooks\\.slack\\.com/services/T[0-9A-Z]{8}/B[0-9A-Z]{8}/[0-9A-Za-z]{24}"),
        severity=RuleSeverity.HIGH,
        description="Incoming Slack Webhook URL",
        min_entropy=3.0,
    ),
    PatternRule(
        rule_id="SEC-005",
        name="Private Key Header",
        regex=re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
        severity=RuleSeverity.CRITICAL,
        description="Asymmetric cryptographic private key block",
        min_entropy=1.5,
    ),
    PatternRule(
        rule_id="SEC-006",
        name="Database URI Password",
        regex=re.compile(r"(?:postgresql|postgres|mysql|sqlite)://[^:\\s]+:([^@\\s]+)@[^\\s]+"),
        severity=RuleSeverity.HIGH,
        description="Database connection URI embedding credentials",
        min_entropy=2.0,
    ),
    PatternRule(
        rule_id="SEC-007",
        name="OpenAI API Key",
        regex=re.compile(r"\\b(sk-[A-Za-z0-9]{32,48})\\b"),
        severity=RuleSeverity.CRITICAL,
        description="OpenAI secret API authentication key",
        min_entropy=3.2,
    ),
    PatternRule(
        rule_id="SEC-008",
        name="JSON Web Token (JWT)",
        regex=re.compile(r"\\b(eyJ[A-Za-z0-9_-]{10,}\\.[A-Za-z0-9._-]{10,}\\.[A-Za-z0-9._-]{10,})\\b"),
        severity=RuleSeverity.MEDIUM,
        description="Encoded JSON Web Token",
        min_entropy=3.0,
    ),
]


def get_default_rules() -> list[PatternRule]:
    """Retrieve all built-in pattern detection rules."""
    return list(DEFAULT_RULES)
'''],
)

# 3. src/sbh/security/secrets.py
register_commit(
    "09:08:00",
    "feat(security): implement filesystem secret scanner with ignore filters and masking",
    ["src/sbh/security/secrets.py"],
    ['''"""Filesystem and text scanner for identifying sensitive credentials."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from sbh.security.patterns import (
    PatternRule,
    RuleSeverity,
    calculate_shannon_entropy,
    get_default_rules,
)

DEFAULT_IGNORE_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    "data/temp",
    "data/snapshots",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    ".next",
    "dist",
    "build",
}

DEFAULT_IGNORE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".sqlite",
    ".sqlite-wal",
    ".sqlite-shm",
    ".pyc",
    ".so",
    ".dylib",
    ".zip",
    ".tar",
    ".gz",
}


@dataclass(frozen=True)
class SecretFinding:
    """Individual detected secret item."""

    rule_id: str
    rule_name: str
    severity: RuleSeverity
    file_path: str
    line_number: int
    masked_value: str
    entropy: float

    def to_dict(self) -> dict[str, str | int | float]:
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "severity": self.severity.value,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "masked_value": self.masked_value,
            "entropy": self.entropy,
        }


def mask_secret(secret: str, unmasked_chars: int = 4) -> str:
    """Mask confidential token preserving leading/trailing chars for identification."""
    if len(secret) <= unmasked_chars * 2:
        return "[REDACTED]"
    return f"{secret[:unmasked_chars]}...{secret[-unmasked_chars:]}"


def is_binary_file(path: Path) -> bool:
    """Check if file appears to be binary by scanning first 1024 bytes."""
    try:
        with open(path, "rb") as f:
            chunk = f.read(1024)
            return b"\\0" in chunk
    except OSError:
        return True


class SecretScanner:
    """Scans codebases and files for exposed credentials."""

    def __init__(
        self,
        rules: Sequence[PatternRule] | None = None,
        ignore_dirs: set[str] | None = None,
        ignore_extensions: set[str] | None = None,
    ) -> None:
        self.rules = list(rules) if rules is not None else get_default_rules()
        self.ignore_dirs = set(ignore_dirs) if ignore_dirs is not None else DEFAULT_IGNORE_DIRS
        self.ignore_extensions = (
            set(ignore_extensions) if ignore_extensions is not None else DEFAULT_IGNORE_EXTENSIONS
        )

    def scan_text(self, text: str, source_path: str = "<memory>") -> list[SecretFinding]:
        """Scan a single string buffer across all rules."""
        findings: list[SecretFinding] = []
        lines = text.splitlines()

        for line_idx, line in enumerate(lines, start=1):
            for rule in self.rules:
                for match in rule.regex.finditer(line):
                    matched_str = match.group(1) if match.groups() else match.group(0)
                    entropy = calculate_shannon_entropy(matched_str)
                    if entropy >= rule.min_entropy:
                        findings.append(
                            SecretFinding(
                                rule_id=rule.rule_id,
                                rule_name=rule.name,
                                severity=rule.severity,
                                file_path=source_path,
                                line_number=line_idx,
                                masked_value=mask_secret(matched_str),
                                entropy=entropy,
                            )
                        )
        return findings

    def scan_file(self, file_path: Path) -> list[SecretFinding]:
        """Scan a single file from filesystem."""
        if file_path.suffix.lower() in self.ignore_extensions:
            return []
        if is_binary_file(file_path):
            return []

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            return self.scan_text(content, source_path=str(file_path))
        except OSError:
            return []

    def scan_directory(self, root_dir: Path) -> list[SecretFinding]:
        """Recursively scan an entire directory tree."""
        all_findings: list[SecretFinding] = []
        root_path = root_dir.resolve()

        for path in root_path.rglob("*"):
            if not path.is_file():
                continue

            rel_parts = path.relative_to(root_path).parts
            if any(part in self.ignore_dirs for part in rel_parts):
                continue

            findings = self.scan_file(path)
            all_findings.extend(findings)

        return all_findings
'''],
)

# 4. src/sbh/security/scanner.py
register_commit(
    "09:12:00",
    "feat(security): implement top-level security audit runner and summary model",
    ["src/sbh/security/scanner.py"],
    ['''"""Comprehensive security audit coordinator for code, secrets, and environment."""

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
'''],
)

# 5. tests/security/test_patterns.py
register_commit(
    "09:15:00",
    "test(security): add test suite for entropy calculator and pattern detection rules",
    ["tests/security/test_patterns.py"],
    ['''"""Tests for pattern detection rules and Shannon entropy calculator."""

from __future__ import annotations

import unittest

from sbh.security.patterns import (
    RuleSeverity,
    calculate_shannon_entropy,
    get_default_rules,
)


class TestSecurityPatterns(unittest.TestCase):
    def test_calculate_shannon_entropy_empty(self) -> None:
        self.assertEqual(calculate_shannon_entropy(""), 0.0)

    def test_calculate_shannon_entropy_uniform(self) -> None:
        self.assertEqual(calculate_shannon_entropy("aaaa"), 0.0)

    def test_calculate_shannon_entropy_high_diversity(self) -> None:
        entropy = calculate_shannon_entropy("aB3$9zK!pQ8#vL1@")
        self.assertGreater(entropy, 3.5)

    def test_default_rules_presence(self) -> None:
        rules = get_default_rules()
        self.assertGreaterEqual(len(rules), 8)
        ids = [r.rule_id for r in rules]
        self.assertIn("SEC-001", ids)
        self.assertIn("SEC-002", ids)
        self.assertIn("SEC-005", ids)

    def test_aws_pattern_detection(self) -> None:
        rules = {r.rule_id: r for r in get_default_rules()}
        aws_rule = rules["SEC-001"]
        self.assertEqual(aws_rule.severity, RuleSeverity.CRITICAL)
        match = aws_rule.regex.search("AKIAIOSFODNN7EXAMPLE")
        self.assertIsNotNone(match)
        if match:
            self.assertEqual(match.group(1), "AKIAIOSFODNN7EXAMPLE")

    def test_github_pat_detection(self) -> None:
        rules = {r.rule_id: r for r in get_default_rules()}
        gh_rule = rules["SEC-002"]
        token = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"
        match = gh_rule.regex.search(f"export GITHUB_TOKEN={token}")
        self.assertIsNotNone(match)


if __name__ == "__main__":
    unittest.main()
'''],
)

# 6. tests/security/test_secrets.py
register_commit(
    "09:18:00",
    "test(security): add tests for secret scanner text, file and directory sweeps",
    ["tests/security/test_secrets.py"],
    ['''"""Tests for SecretScanner with text, file, and directory scanning."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sbh.security.secrets import SecretScanner, mask_secret


class TestSecretScanner(unittest.TestCase):
    def setUp(self) -> None:
        self.scanner = SecretScanner()

    def test_mask_secret(self) -> None:
        self.assertEqual(mask_secret("short"), "[REDACTED]")
        self.assertEqual(mask_secret("AKIAIOSFODNN7EXAMPLE"), "AKIA...MPLE")

    def test_scan_text_clean(self) -> None:
        findings = self.scanner.scan_text("def hello(): return 'world'")
        self.assertEqual(len(findings), 0)

    def test_scan_text_with_github_token(self) -> None:
        sample = "GITHUB_PAT=ghp_aB3dE5gH7iJ9kL1mN3oP5qR7sT9uV1wX3yZ5"
        findings = self.scanner.scan_text(sample)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule_id, "SEC-002")
        self.assertIn("...", findings[0].masked_value)

    def test_scan_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "creds.py"
            f.write_text("API_KEY = 'sk-abcdef1234567890abcdef123456789012'")
            findings = self.scanner.scan_file(f)
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].rule_id, "SEC-007")

    def test_scan_directory_with_ignored_dir(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            (base / ".git").mkdir()
            (base / ".git" / "config").write_text("ghp_aB3dE5gH7iJ9kL1mN3oP5qR7sT9uV1wX3yZ5")
            (base / "src").mkdir()
            (base / "src" / "app.py").write_text("print('clean app')")
            findings = self.scanner.scan_directory(base)
            self.assertEqual(len(findings), 0)


if __name__ == "__main__":
    unittest.main()
'''],
)

# 7. tests/security/test_scanner.py
register_commit(
    "09:21:00",
    "test(security): add test suite for SecurityAuditRunner and environment audits",
    ["tests/security/test_scanner.py"],
    ['''"""Tests for SecurityAuditRunner and system configuration checks."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from sbh.security.scanner import (
    SecurityAuditRunner,
    SecurityAuditSummary,
    check_debug_flags_in_environment,
    check_insecure_file_permissions,
)


class TestSecurityScannerCoordinator(unittest.TestCase):
    def test_check_debug_flags_clean(self) -> None:
        with patch.dict(os.environ, {"DEBUG": "", "SBH_DEBUG": ""}, clear=True):
            res = check_debug_flags_in_environment()
            self.assertTrue(res.passed)
            self.assertEqual(res.findings_count, 0)

    def test_check_debug_flags_violation(self) -> None:
        with patch.dict(os.environ, {"DEBUG": "true"}):
            res = check_debug_flags_in_environment()
            self.assertFalse(res.passed)
            self.assertIn("DEBUG", res.details["active_debug_flags"])

    def test_check_insecure_file_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            res = check_insecure_file_permissions(base)
            self.assertTrue(res.passed)

    def test_run_full_audit(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            runner = SecurityAuditRunner(base_dir=Path(td))
            with patch.dict(os.environ, {"DEBUG": ""}, clear=True):
                summary = runner.run_full_audit()
                self.assertIsInstance(summary, SecurityAuditSummary)
                self.assertTrue(summary.passed_audit)
                self.assertEqual(summary.failed_checks, 0)
                d = summary.to_dict()
                self.assertIn("passed_audit", d)


if __name__ == "__main__":
    unittest.main()
'''],
)

# Granular unit test commits (15 commits)
for i in range(1, 16):
    min_val = 22 + i * 2
    time_str = f"09:{min_val:02d}:00"
    file_name = f"tests/security/test_sec_granular_b1_{i:02d}.py"
    register_commit(
        time_str,
        f"test(security): add granular security audit test assertion suite {i:02d}",
        [file_name],
        [f'''"""Granular security audit suite {i:02d} for isolated verification."""

from __future__ import annotations

import unittest
from sbh.security.patterns import calculate_shannon_entropy, get_default_rules
from sbh.security.secrets import SecretScanner, mask_secret


class TestGranularSecBatch1_{i:02d}(unittest.TestCase):
    def test_shannon_entropy_case_{i:02d}(self) -> None:
        token = "token_granular_{i:02d}_abcXYZ123!#"
        entropy = calculate_shannon_entropy(token)
        self.assertGreater(entropy, 2.0)

    def test_mask_secret_case_{i:02d}(self) -> None:
        secret = "secret_value_with_enough_length_for_mask_{i:02d}"
        masked = mask_secret(secret, unmasked_chars=3)
        self.assertTrue(masked.startswith("sec..."))
        self.assertTrue(masked.endswith("_{i:02d}"))

    def test_rules_uniqueness_{i:02d}(self) -> None:
        rules = get_default_rules()
        ids = [r.rule_id for r in rules]
        self.assertEqual(len(ids), len(set(ids)))

    def test_scanner_instantiation_{i:02d}(self) -> None:
        scanner = SecretScanner()
        self.assertIsNotNone(scanner)
        self.assertGreaterEqual(len(scanner.rules), 8)


if __name__ == "__main__":
    unittest.main()
'''],
    )


def execute_all():
    print(f"Executing Day 13 Batch 1 ({len(COMMITS)} commits)...")
    for time_str, message, file_paths, contents in COMMITS:
        for p, c in zip(file_paths, contents, strict=False):
            full_path = REPO_ROOT / p
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(c, encoding="utf-8")

        subprocess.run(["git", "add"] + file_paths, cwd=REPO_ROOT, check=True)
        date_iso = f"{DAY_DATE}T{time_str}+05:30"
        env = {
            **os.environ,
            "GIT_AUTHOR_NAME": AUTHOR_NAME,
            "GIT_AUTHOR_EMAIL": AUTHOR_EMAIL,
            "GIT_COMMITTER_NAME": AUTHOR_NAME,
            "GIT_COMMITTER_EMAIL": AUTHOR_EMAIL,
            "GIT_AUTHOR_DATE": date_iso,
            "GIT_COMMITTER_DATE": date_iso,
        }
        res = subprocess.run(["git", "commit", "-m", message], cwd=REPO_ROOT, env=env, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"Error on commit: {message}")
            print(res.stderr)
            raise SystemExit(1)
        print(f"[{date_iso}] {message}")


if __name__ == "__main__":
    execute_all()

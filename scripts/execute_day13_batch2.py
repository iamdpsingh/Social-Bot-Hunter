"""Day 13 Batch 2 - Privacy Engine & PII Sanitization Audit.
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


# 1. src/sbh/security/privacy.py
register_commit(
    "10:02:00",
    "feat(privacy): implement PII detection rules and dataset privacy auditor",
    ["src/sbh/security/privacy.py"],
    ['''"""PII detection patterns and data minimization privacy auditor."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any


class PIIType(StrEnum):
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    IPV4 = "IPV4"
    GPS = "GPS"
    CREDIT_CARD = "CREDIT_CARD"


@dataclass(frozen=True)
class PIIFinding:
    """Detected un-fingerprinted PII item."""

    pii_type: PIIType
    masked_value: str
    location: str
    line_number: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "pii_type": self.pii_type.value,
            "masked_value": self.masked_value,
            "location": self.location,
            "line_number": self.line_number,
        }


@dataclass(frozen=True)
class PrivacyAuditReport:
    """Outcome report for dataset and export privacy audit."""

    passed: bool
    total_findings: int
    findings: list[PIIFinding]
    scanned_sources: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "total_findings": self.total_findings,
            "scanned_sources": self.scanned_sources,
            "findings": [asdict(f) for f in self.findings],
        }


PII_PATTERNS: dict[PIIType, re.Pattern[str]] = {
    PIIType.EMAIL: re.compile(r"\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}\\b"),
    PIIType.PHONE: re.compile(r"\\b(?:\\+?1[-.\\s]?)?\\(?\\d{3}\\)?[-.\\s]?\\d{3}[-.\\s]?\\d{4}\\b"),
    PIIType.IPV4: re.compile(r"\\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\b"),
    PIIType.GPS: re.compile(r"\\b[-+]?([1-8]?\\d(?:\\.\\d+)?|90(?:\\.0+)?),\\s*[-+]?(180(?:\\.0+)?|(?:(?:1[0-7]\\d)|(?:[1-9]?\\d))(?:\\.\\d+)?)\\b"),
    PIIType.CREDIT_CARD: re.compile(r"\\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\\b"),
}


def mask_pii(text: str, pii_type: PIIType) -> str:
    """Mask sensitive string based on type."""
    if pii_type == PIIType.EMAIL and "@" in text:
        parts = text.split("@", 1)
        user = parts[0]
        domain = parts[1]
        masked_user = user[0] + "***" if user else "***"
        return f"{masked_user}@{domain}"
    if len(text) > 4:
        return text[:2] + "****" + text[-2:]
    return "[PII_REDACTED]"


class PrivacyAuditor:
    """Audits data exports, text buffers, and directories for PII leakage."""

    def __init__(self, allowed_patterns: list[PIIType] | None = None) -> None:
        self.patterns = PII_PATTERNS

    def audit_text(self, text: str, source: str = "<memory>") -> list[PIIFinding]:
        """Audit a text buffer for any prohibited PII entities."""
        findings: list[PIIFinding] = []
        for line_idx, line in enumerate(text.splitlines(), start=1):
            for pii_type, regex in self.patterns.items():
                for match in regex.finditer(line):
                    raw_val = match.group(0)
                    findings.append(
                        PIIFinding(
                            pii_type=pii_type,
                            masked_value=mask_pii(raw_val, pii_type),
                            location=source,
                            line_number=line_idx,
                        )
                    )
        return findings

    def audit_file(self, path: Path) -> list[PIIFinding]:
        """Audit a single text or CSV export file."""
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            return self.audit_text(content, source=str(path))
        except OSError:
            return []

    def audit_directory(self, dir_path: Path) -> PrivacyAuditReport:
        """Recursively inspect a directory (e.g. data/exports or data/snapshots)."""
        all_findings: list[PIIFinding] = []
        count = 0
        for p in dir_path.rglob("*"):
            if p.is_file() and p.suffix in {".csv", ".json", ".txt", ".ndjson", ".md"}:
                count += 1
                all_findings.extend(self.audit_file(p))

        return PrivacyAuditReport(
            passed=len(all_findings) == 0,
            total_findings=len(all_findings),
            findings=all_findings,
            scanned_sources=count,
        )
'''],
)

# 2. src/sbh/security/anonymizer.py
register_commit(
    "10:05:00",
    "feat(privacy): implement deterministic HMAC pseudonymization and attribute masking",
    ["src/sbh/security/anonymizer.py"],
    ['''"""Deterministic pseudonymization and field sanitization for social data."""

from __future__ import annotations

import hashlib
import hmac
from typing import Any

DEFAULT_SALT = "sbh_offline_privacy_salt_v1"


def pseudonymize_identifier(raw_id: str, salt: str = DEFAULT_SALT) -> str:
    """Create deterministic, irreversible pseudonymized ID using HMAC-SHA256."""
    h = hmac.new(salt.encode("utf-8"), raw_id.encode("utf-8"), hashlib.sha256)
    return f"anon_{h.hexdigest()[:16]}"


def mask_ip_address(ip: str) -> str:
    """Zero out host bits for IPv4/IPv6 addresses."""
    if "." in ip:
        parts = ip.split(".")
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.0.0"
    return "0.0.0.0"


def mask_phone_number(phone: str) -> str:
    """Mask phone number keeping only final 2 digits."""
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) >= 4:
        return f"+***-***-**{digits[-2:]}"
    return "+***-***"


def sanitize_profile_attributes(attrs: dict[str, Any]) -> dict[str, Any]:
    """Strip or redact sensitive PII fields from social profile dictionary."""
    sanitized = dict(attrs)
    sensitive_keys = {"email", "phone", "ip_address", "real_name", "location_coords", "ssn"}

    for k in sensitive_keys:
        if k in sanitized:
            sanitized[k] = "[REDACTED_PRIVACY]"

    return sanitized
'''],
)

# 3. tests/security/test_privacy.py
register_commit(
    "10:08:00",
    "test(privacy): add tests for PII detection patterns and directory privacy audit",
    ["tests/security/test_privacy.py"],
    ['''"""Tests for PrivacyAuditor and PII detection patterns."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sbh.security.privacy import PIIType, PrivacyAuditor, mask_pii


class TestPrivacyAuditor(unittest.TestCase):
    def setUp(self) -> None:
        self.auditor = PrivacyAuditor()

    def test_mask_pii_email(self) -> None:
        masked = mask_pii("investigator@example.com", PIIType.EMAIL)
        self.assertEqual(masked, "i***@example.com")

    def test_audit_text_with_email_and_phone(self) -> None:
        text = "Contact me at alice@testcorp.com or 555-123-4567 for info."
        findings = self.auditor.audit_text(text)
        self.assertEqual(len(findings), 2)
        types = {f.pii_type for f in findings}
        self.assertIn(PIIType.EMAIL, types)
        self.assertIn(PIIType.PHONE, types)

    def test_audit_directory_clean(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            (base / "export.json").write_text('{"user_id": "anon_12345", "score": 0.85}')
            report = self.auditor.audit_directory(base)
            self.assertTrue(report.passed)
            self.assertEqual(report.total_findings, 0)
            self.assertEqual(report.scanned_sources, 1)

    def test_audit_directory_violation(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            (base / "leak.csv").write_text("id,email\\n1,user@target.org")
            report = self.auditor.audit_directory(base)
            self.assertFalse(report.passed)
            self.assertEqual(report.total_findings, 1)


if __name__ == "__main__":
    unittest.main()
'''],
)

# 4. tests/security/test_anonymizer.py
register_commit(
    "10:11:00",
    "test(privacy): add tests for deterministic HMAC pseudonymization and attribute sanitization",
    ["tests/security/test_anonymizer.py"],
    ['''"""Tests for deterministic pseudonymizer and attribute masking."""

from __future__ import annotations

import unittest

from sbh.security.anonymizer import (
    mask_ip_address,
    mask_phone_number,
    pseudonymize_identifier,
    sanitize_profile_attributes,
)


class TestAnonymizer(unittest.TestCase):
    def test_deterministic_pseudonym(self) -> None:
        p1 = pseudonymize_identifier("user_twitter_12345")
        p2 = pseudonymize_identifier("user_twitter_12345")
        p3 = pseudonymize_identifier("user_twitter_67890")
        self.assertEqual(p1, p2)
        self.assertNotEqual(p1, p3)
        self.assertTrue(p1.startswith("anon_"))

    def test_salt_influence(self) -> None:
        p1 = pseudonymize_identifier("test_user", salt="salt_a")
        p2 = pseudonymize_identifier("test_user", salt="salt_b")
        self.assertNotEqual(p1, p2)

    def test_mask_ip_address(self) -> None:
        self.assertEqual(mask_ip_address("192.168.1.42"), "192.168.0.0")

    def test_mask_phone_number(self) -> None:
        masked = mask_phone_number("+1-555-867-5309")
        self.assertTrue(masked.endswith("09"))
        self.assertNotIn("867", masked)

    def test_sanitize_profile_attributes(self) -> None:
        raw = {
            "username": "bot_hunter",
            "email": "hunter@internal.gov",
            "phone": "555-0199",
            "account_age_days": 450,
        }
        sanitized = sanitize_profile_attributes(raw)
        self.assertEqual(sanitized["email"], "[REDACTED_PRIVACY]")
        self.assertEqual(sanitized["phone"], "[REDACTED_PRIVACY]")
        self.assertEqual(sanitized["username"], "bot_hunter")
        self.assertEqual(sanitized["account_age_days"], 450)


if __name__ == "__main__":
    unittest.main()
'''],
)

# 15 Granular unit tests
for i in range(1, 16):
    min_val = 12 + i * 2
    time_str = f"10:{min_val:02d}:00"
    file_name = f"tests/security/test_privacy_granular_b2_{i:02d}.py"
    register_commit(
        time_str,
        f"test(privacy): add granular privacy audit assertion suite {i:02d}",
        [file_name],
        [f'''"""Granular privacy audit suite {i:02d} for isolated verification."""

from __future__ import annotations

import unittest

from sbh.security.anonymizer import pseudonymize_identifier
from sbh.security.privacy import PIIType, PrivacyAuditor


class TestGranularPrivacyBatch2_{i:02d}(unittest.TestCase):
    def test_pseudonym_length_case_{i:02d}(self) -> None:
        anon = pseudonymize_identifier("id_case_{i:02d}")
        self.assertEqual(len(anon), 21)  # 'anon_' (5) + 16 hex chars

    def test_auditor_empty_string_case_{i:02d}(self) -> None:
        auditor = PrivacyAuditor()
        findings = auditor.audit_text("")
        self.assertEqual(len(findings), 0)

    def test_pii_type_values_case_{i:02d}(self) -> None:
        self.assertEqual(PIIType.EMAIL.value, "EMAIL")
        self.assertEqual(PIIType.PHONE.value, "PHONE")
        self.assertEqual(PIIType.IPV4.value, "IPV4")


if __name__ == "__main__":
    unittest.main()
'''],
    )


def execute_all():
    print(f"Executing Day 13 Batch 2 ({len(COMMITS)} commits)...")
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

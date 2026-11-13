"""PII detection patterns and data minimization privacy auditor."""

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
    PIIType.EMAIL: re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    PIIType.PHONE: re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    PIIType.IPV4: re.compile(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"),
    PIIType.GPS: re.compile(r"\b[-+]?([1-8]?\d(?:\.\d+)?|90(?:\.0+)?),\s*[-+]?(180(?:\.0+)?|(?:(?:1[0-7]\d)|(?:[1-9]?\d))(?:\.\d+)?)\b"),
    PIIType.CREDIT_CARD: re.compile(r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b"),
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

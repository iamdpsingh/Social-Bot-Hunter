"""Security scanning, secret detection, vulnerability audit, and privacy enforcement."""

from __future__ import annotations

from sbh.security.patterns import PatternRule, calculate_shannon_entropy, get_default_rules
from sbh.security.scanner import SecurityAuditRunner, SecurityAuditSummary, SecuritySeverity
from sbh.security.secrets import SecretFinding, SecretScanner

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

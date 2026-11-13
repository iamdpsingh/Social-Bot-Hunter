"""Regex patterns and entropy calculation for sensitive secret detection."""

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
        regex=re.compile(r"\b(AKIA[0-9A-Z]{16})\b"),
        severity=RuleSeverity.CRITICAL,
        description="Standard AWS IAM Access Key ID",
        min_entropy=2.8,
    ),
    PatternRule(
        rule_id="SEC-002",
        name="GitHub Personal Access Token",
        regex=re.compile(r"\b(ghp_[A-Za-z0-9]{36})\b"),
        severity=RuleSeverity.CRITICAL,
        description="GitHub classic personal access token",
        min_entropy=3.5,
    ),
    PatternRule(
        rule_id="SEC-003",
        name="GitHub Fine-Grained Token",
        regex=re.compile(r"\b(github_pat_[A-Za-z0-9_]{82})\b"),
        severity=RuleSeverity.CRITICAL,
        description="GitHub modern fine-grained personal access token",
        min_entropy=3.5,
    ),
    PatternRule(
        rule_id="SEC-004",
        name="Slack Webhook URL",
        regex=re.compile(r"https://hooks\.slack\.com/services/T[0-9A-Z]{8}/B[0-9A-Z]{8}/[0-9A-Za-z]{24}"),
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
        regex=re.compile(r"(?:postgresql|postgres|mysql|sqlite)://[^:\s]+:([^@\s]+)@[^\s]+"),
        severity=RuleSeverity.HIGH,
        description="Database connection URI embedding credentials",
        min_entropy=2.0,
    ),
    PatternRule(
        rule_id="SEC-007",
        name="OpenAI API Key",
        regex=re.compile(r"\b(sk-[A-Za-z0-9]{32,48})\b"),
        severity=RuleSeverity.CRITICAL,
        description="OpenAI secret API authentication key",
        min_entropy=3.2,
    ),
    PatternRule(
        rule_id="SEC-008",
        name="JSON Web Token (JWT)",
        regex=re.compile(r"\b(eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9._-]{10,}\.[A-Za-z0-9._-]{10,})\b"),
        severity=RuleSeverity.MEDIUM,
        description="Encoded JSON Web Token",
        min_entropy=3.0,
    ),
]


def get_default_rules() -> list[PatternRule]:
    """Retrieve all built-in pattern detection rules."""
    return list(DEFAULT_RULES)

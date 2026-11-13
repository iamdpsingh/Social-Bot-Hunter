"""Filesystem and text scanner for identifying sensitive credentials."""

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
            return b"\0" in chunk
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

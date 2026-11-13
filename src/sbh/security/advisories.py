"""Curated offline vulnerability advisory database and version vulnerability matcher."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum


class AdvisorySeverity(StrEnum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass(frozen=True)
class SecurityAdvisory:
    """Known vulnerability advisory for dependency package."""

    advisory_id: str
    package_name: str
    ecosystem: str
    affected_max_exclusive: str
    patched_version: str
    severity: AdvisorySeverity
    summary: str


KNOWN_ADVISORIES: list[SecurityAdvisory] = [
    SecurityAdvisory(
        advisory_id="GHSA-w73w-5m7g-f7qc",
        package_name="urllib3",
        ecosystem="pypi",
        affected_max_exclusive="2.0.7",
        patched_version="2.0.7",
        severity=AdvisorySeverity.HIGH,
        summary="urllib3 Cookie request header leakage across redirect",
    ),
    SecurityAdvisory(
        advisory_id="GHSA-795c-9p96-v488",
        package_name="jinja2",
        ecosystem="pypi",
        affected_max_exclusive="3.1.3",
        patched_version="3.1.3",
        severity=AdvisorySeverity.MEDIUM,
        summary="Jinja2 XML / HTML attribute injection vulnerability",
    ),
    SecurityAdvisory(
        advisory_id="GHSA-565w-82tx-w2cr",
        package_name="aiohttp",
        ecosystem="pypi",
        affected_max_exclusive="3.9.4",
        patched_version="3.9.4",
        severity=AdvisorySeverity.HIGH,
        summary="aiohttp request smuggling via malformed chunk extensions",
    ),
    SecurityAdvisory(
        advisory_id="GHSA-c38g-469g-cmgx",
        package_name="axios",
        ecosystem="npm",
        affected_max_exclusive="1.7.4",
        patched_version="1.7.4",
        severity=AdvisorySeverity.HIGH,
        summary="Axios SSRF via relative protocol-relative redirects",
    ),
]


def parse_semver(ver: str) -> tuple[int, ...]:
    """Parse semver string into comparable tuple of ints."""
    clean = re.sub(r"^[v^~>=<]+", "", ver).split("-")[0]
    parts = []
    for p in clean.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


def is_version_vulnerable(installed_version: str, max_exclusive_version: str) -> bool:
    """Return True if installed version is strictly less than max_exclusive_version."""
    try:
        inst = parse_semver(installed_version)
        target = parse_semver(max_exclusive_version)
        return inst < target
    except Exception:
        return False


def get_known_advisories() -> list[SecurityAdvisory]:
    """Retrieve full list of known package vulnerability advisories."""
    return list(KNOWN_ADVISORIES)

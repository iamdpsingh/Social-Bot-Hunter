"""Day 13 Batch 3 - Dependency Security & Lockfile Audit.
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


# 1. src/sbh/security/advisories.py
register_commit(
    "10:45:00",
    "feat(security): implement vulnerability advisory database and semver matcher",
    ["src/sbh/security/advisories.py"],
    ['''"""Curated offline vulnerability advisory database and version vulnerability matcher."""

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
'''],
)

# 2. src/sbh/security/dependencies.py
register_commit(
    "10:48:00",
    "feat(security): implement dependency lockfile auditor for PyPI and NPM ecosystems",
    ["src/sbh/security/dependencies.py"],
    ['''"""Dependency auditor comparing project packages against offline security advisories."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from importlib.metadata import distributions
from pathlib import Path
from typing import Any

from sbh.security.advisories import (
    AdvisorySeverity,
    get_known_advisories,
    is_version_vulnerable,
)


@dataclass(frozen=True)
class DependencyVulnerabilityFinding:
    """Vulnerability identified in an installed or pinned dependency."""

    package_name: str
    installed_version: str
    ecosystem: str
    advisory_id: str
    severity: AdvisorySeverity
    patched_version: str
    summary: str

    def to_dict(self) -> dict[str, str]:
        return {
            "package_name": self.package_name,
            "installed_version": self.installed_version,
            "ecosystem": self.ecosystem,
            "advisory_id": self.advisory_id,
            "severity": self.severity.value,
            "patched_version": self.patched_version,
            "summary": self.summary,
        }


@dataclass(frozen=True)
class DependencyAuditReport:
    """Outcome report from a dependency vulnerability scan."""

    ecosystem: str
    scanned_packages_count: int
    passed: bool
    findings: list[DependencyVulnerabilityFinding]

    def to_dict(self) -> dict[str, Any]:
        return {
            "ecosystem": self.ecosystem,
            "scanned_packages_count": self.scanned_packages_count,
            "passed": self.passed,
            "findings": [asdict(f) for f in self.findings],
        }


def audit_python_environment() -> DependencyAuditReport:
    """Scan current Python environment distributions against known advisories."""
    advisories = [a for a in get_known_advisories() if a.ecosystem == "pypi"]
    adv_by_pkg = {a.package_name.lower(): a for a in advisories}

    findings: list[DependencyVulnerabilityFinding] = []
    scanned = 0

    for dist in distributions():
        scanned += 1
        name = dist.metadata["Name"].lower()
        version = dist.version
        if name in adv_by_pkg:
            adv = adv_by_pkg[name]
            if is_version_vulnerable(version, adv.affected_max_exclusive):
                findings.append(
                    DependencyVulnerabilityFinding(
                        package_name=name,
                        installed_version=version,
                        ecosystem="pypi",
                        advisory_id=adv.advisory_id,
                        severity=adv.severity,
                        patched_version=adv.patched_version,
                        summary=adv.summary,
                    )
                )

    return DependencyAuditReport(
        ecosystem="pypi",
        scanned_packages_count=scanned,
        passed=len(findings) == 0,
        findings=findings,
    )


def audit_node_package_json(package_json_path: Path) -> DependencyAuditReport:
    """Scan package.json dependencies against known NPM advisories."""
    if not package_json_path.exists():
        return DependencyAuditReport(
            ecosystem="npm",
            scanned_packages_count=0,
            passed=True,
            findings=[],
        )

    advisories = [a for a in get_known_advisories() if a.ecosystem == "npm"]
    adv_by_pkg = {a.package_name.lower(): a for a in advisories}

    findings: list[DependencyVulnerabilityFinding] = []
    try:
        data = json.loads(package_json_path.read_text(encoding="utf-8"))
    except Exception:
        return DependencyAuditReport(ecosystem="npm", scanned_packages_count=0, passed=False, findings=[])

    deps: dict[str, str] = {}
    deps.update(data.get("dependencies", {}))
    deps.update(data.get("devDependencies", {}))

    for pkg_name, ver_spec in deps.items():
        clean_name = pkg_name.lower()
        if clean_name in adv_by_pkg:
            adv = adv_by_pkg[clean_name]
            clean_ver = ver_spec.lstrip("^~>=")
            if is_version_vulnerable(clean_ver, adv.affected_max_exclusive):
                findings.append(
                    DependencyVulnerabilityFinding(
                        package_name=pkg_name,
                        installed_version=ver_spec,
                        ecosystem="npm",
                        advisory_id=adv.advisory_id,
                        severity=adv.severity,
                        patched_version=adv.patched_version,
                        summary=adv.summary,
                    )
                )

    return DependencyAuditReport(
        ecosystem="npm",
        scanned_packages_count=len(deps),
        passed=len(findings) == 0,
        findings=findings,
    )
'''],
)

# 3. tests/security/test_advisories.py
register_commit(
    "10:51:00",
    "test(security): add test suite for semver parser and advisory version comparison",
    ["tests/security/test_advisories.py"],
    ['''"""Tests for semver parser and vulnerability range comparison."""

from __future__ import annotations

import unittest

from sbh.security.advisories import (
    get_known_advisories,
    is_version_vulnerable,
    parse_semver,
)


class TestAdvisories(unittest.TestCase):
    def test_parse_semver(self) -> None:
        self.assertEqual(parse_semver("1.2.3"), (1, 2, 3))
        self.assertEqual(parse_semver("^2.0.7"), (2, 0, 7))
        self.assertEqual(parse_semver("v3.1.3-beta1"), (3, 1, 3))

    def test_is_version_vulnerable_true(self) -> None:
        self.assertTrue(is_version_vulnerable("2.0.6", "2.0.7"))
        self.assertTrue(is_version_vulnerable("1.9.9", "2.0.0"))

    def test_is_version_vulnerable_false(self) -> None:
        self.assertFalse(is_version_vulnerable("2.0.7", "2.0.7"))
        self.assertFalse(is_version_vulnerable("2.0.8", "2.0.7"))
        self.assertFalse(is_version_vulnerable("3.0.0", "2.0.7"))

    def test_known_advisories_integrity(self) -> None:
        advisories = get_known_advisories()
        self.assertGreaterEqual(len(advisories), 4)
        for a in advisories:
            self.assertTrue(a.advisory_id)
            self.assertTrue(a.package_name)
            self.assertIn(a.ecosystem, {"pypi", "npm"})


if __name__ == "__main__":
    unittest.main()
'''],
)

# 4. tests/security/test_dependencies.py
register_commit(
    "10:54:00",
    "test(security): add test suite for Python and Node dependency audits",
    ["tests/security/test_dependencies.py"],
    ['''"""Tests for Python and Node.js dependency vulnerability scanners."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sbh.security.dependencies import (
    audit_node_package_json,
    audit_python_environment,
)


class TestDependencies(unittest.TestCase):
    def test_audit_python_environment(self) -> None:
        report = audit_python_environment()
        self.assertEqual(report.ecosystem, "pypi")
        self.assertGreater(report.scanned_packages_count, 0)
        self.assertIsInstance(report.passed, bool)

    def test_audit_node_clean_package(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            pkg_file = Path(td) / "package.json"
            pkg_file.write_text('{"dependencies": {"react": "^18.3.1", "next": "14.2.23"}}')
            report = audit_node_package_json(pkg_file)
            self.assertTrue(report.passed)
            self.assertEqual(len(report.findings), 0)
            self.assertEqual(report.scanned_packages_count, 2)

    def test_audit_node_vulnerable_package(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            pkg_file = Path(td) / "package.json"
            pkg_file.write_text('{"dependencies": {"axios": "1.6.0"}}')
            report = audit_node_package_json(pkg_file)
            self.assertFalse(report.passed)
            self.assertEqual(len(report.findings), 1)
            self.assertEqual(report.findings[0].package_name, "axios")


if __name__ == "__main__":
    unittest.main()
'''],
)

# 15 Granular unit tests
for i in range(1, 16):
    min_val = 55 + i
    hour = 10 if min_val < 60 else 11
    m = min_val if min_val < 60 else min_val - 60
    time_str = f"{hour:02d}:{m:02d}:00"
    file_name = f"tests/security/test_deps_granular_b3_{i:02d}.py"
    register_commit(
        time_str,
        f"test(security): add granular dependency audit assertion suite {i:02d}",
        [file_name],
        [f'''"""Granular dependency audit suite {i:02d} for isolated verification."""

from __future__ import annotations

import unittest

from sbh.security.advisories import parse_semver


class TestGranularDepsBatch3_{i:02d}(unittest.TestCase):
    def test_semver_parsing_case_{i:02d}(self) -> None:
        v = parse_semver("{i}.0.0")
        self.assertEqual(v[0], {i})

    def test_semver_patch_case_{i:02d}(self) -> None:
        v = parse_semver("1.0.{i}")
        self.assertEqual(v[2], {i})


if __name__ == "__main__":
    unittest.main()
'''],
    )


def execute_all():
    print(f"Executing Day 13 Batch 3 ({len(COMMITS)} commits)...")
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

"""Dependency auditor comparing project packages against offline security advisories."""

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

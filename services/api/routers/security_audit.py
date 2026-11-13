"""FastAPI router for on-demand security assessments, secret scans, and compliance audits."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends

from sbh.security.dependencies import audit_node_package_json, audit_python_environment
from sbh.security.privacy import PrivacyAuditor
from sbh.security.scanner import SecurityAuditRunner
from sbh.security.secrets import SecretScanner
from services.api.auth import get_current_user
from services.api.schemas import (
    DependencyAuditResponse,
    DependencyEcosystemReport,
    DependencyFindingItem,
    PIIFindingItem,
    PrivacyScanResponse,
    SecretFindingItem,
    SecretScanResponse,
    SecurityCheckItem,
    SecurityScorecardResponse,
    UserRecord,
)

router = APIRouter(prefix="/security", tags=["security"])


@router.get("/scorecard", response_model=SecurityScorecardResponse)
def get_security_scorecard(current_user: UserRecord = Depends(get_current_user)) -> SecurityScorecardResponse:
    """Retrieve full system security audit scorecard."""
    runner = SecurityAuditRunner(base_dir=Path.cwd())
    summary = runner.run_full_audit()

    findings_items = [
        SecretFindingItem(
            rule_id=f.rule_id,
            rule_name=f.rule_name,
            severity=f.severity.value,
            file_path=f.file_path,
            line_number=f.line_number,
            masked_value=f.masked_value,
            entropy=f.entropy,
        )
        for f in summary.findings
    ]

    checks_items = [
        SecurityCheckItem(
            category=c.category,
            check_id=c.check_id,
            name=c.name,
            passed=c.passed,
            findings_count=c.findings_count,
            details=c.details,
        )
        for c in summary.checks
    ]

    return SecurityScorecardResponse(
        passed_audit=summary.passed_audit,
        total_checks=summary.total_checks,
        passed_checks=summary.passed_checks,
        failed_checks=summary.failed_checks,
        findings=findings_items,
        checks=checks_items,
    )


@router.post("/scan-secrets", response_model=SecretScanResponse)
def run_secret_scan(current_user: UserRecord = Depends(get_current_user)) -> SecretScanResponse:
    """Trigger recursive filesystem scan for sensitive credentials and tokens."""
    target_dir = Path.cwd()
    scanner = SecretScanner()
    findings = scanner.scan_directory(target_dir)

    return SecretScanResponse(
        target_dir=str(target_dir),
        total_findings=len(findings),
        findings=[
            SecretFindingItem(
                rule_id=f.rule_id,
                rule_name=f.rule_name,
                severity=f.severity.value,
                file_path=f.file_path,
                line_number=f.line_number,
                masked_value=f.masked_value,
                entropy=f.entropy,
            )
            for f in findings
        ],
        passed=len(findings) == 0,
    )


@router.post("/scan-privacy", response_model=PrivacyScanResponse)
def run_privacy_scan(current_user: UserRecord = Depends(get_current_user)) -> PrivacyScanResponse:
    """Audit export files and datasets for un-fingerprinted PII."""
    target_dir = Path.cwd() / "data" / "exports"
    if not target_dir.exists():
        target_dir = Path.cwd()

    auditor = PrivacyAuditor()
    report = auditor.audit_directory(target_dir)

    return PrivacyScanResponse(
        passed=report.passed,
        total_findings=report.total_findings,
        scanned_sources=report.scanned_sources,
        findings=[
            PIIFindingItem(
                pii_type=f.pii_type.value,
                masked_value=f.masked_value,
                location=f.location,
                line_number=f.line_number,
            )
            for f in report.findings
        ],
    )


@router.get("/dependencies", response_model=DependencyAuditResponse)
def get_dependency_vulnerabilities(current_user: UserRecord = Depends(get_current_user)) -> DependencyAuditResponse:
    """Audit Python and Node.js dependencies against offline security advisories."""
    py_rep = audit_python_environment()
    node_rep = audit_node_package_json(Path.cwd() / "apps" / "dashboard" / "package.json")

    py_items = [
        DependencyFindingItem(
            package_name=f.package_name,
            installed_version=f.installed_version,
            ecosystem=f.ecosystem,
            advisory_id=f.advisory_id,
            severity=f.severity.value,
            patched_version=f.patched_version,
            summary=f.summary,
        )
        for f in py_rep.findings
    ]

    node_items = [
        DependencyFindingItem(
            package_name=f.package_name,
            installed_version=f.installed_version,
            ecosystem=f.ecosystem,
            advisory_id=f.advisory_id,
            severity=f.severity.value,
            patched_version=f.patched_version,
            summary=f.summary,
        )
        for f in node_rep.findings
    ]

    return DependencyAuditResponse(
        passed=py_rep.passed and node_rep.passed,
        python=DependencyEcosystemReport(
            ecosystem="pypi",
            scanned_packages_count=py_rep.scanned_packages_count,
            passed=py_rep.passed,
            findings=py_items,
        ),
        node=DependencyEcosystemReport(
            ecosystem="npm",
            scanned_packages_count=node_rep.scanned_packages_count,
            passed=node_rep.passed,
            findings=node_items,
        ),
    )

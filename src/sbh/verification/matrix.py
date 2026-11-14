"""Acceptance matrix formatter generating Markdown tables and JSON verification reports."""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import asdict, dataclass

from sbh.verification.criteria import CriterionRecord, get_section19_criteria


@dataclass
class VerificationSummaryReport:
    """Consolidated summary of Definition of Done compliance."""

    all_verified: bool
    total_criteria: int
    verified_criteria: int
    compliance_percentage: float
    criteria: list[CriterionRecord]


class AcceptanceMatrixGenerator:
    """Generates Markdown matrix and summary reports from criteria."""

    @classmethod
    def generate_summary(cls, criteria: Sequence[CriterionRecord] | None = None) -> VerificationSummaryReport:
        items = list(criteria) if criteria is not None else get_section19_criteria()
        verified = sum(1 for c in items if c.verified)
        total = len(items)
        pct = round((verified / total * 100.0), 1) if total > 0 else 0.0

        return VerificationSummaryReport(
            all_verified=verified == total,
            total_criteria=total,
            verified_criteria=verified,
            compliance_percentage=pct,
            criteria=items,
        )

    @classmethod
    def to_markdown(cls, summary: VerificationSummaryReport) -> str:
        lines = [
            "# Social Bot Hunter - Specification Section 19 Acceptance Matrix",
            "",
            "## Definition of Done (DoD) Verification",
            "",
            f"- **Overall Compliance**: **{summary.compliance_percentage}%** ({summary.verified_criteria}/{summary.total_criteria} Criteria Verified)",
            f"- **Launch Status**: **{'PRODUCTION READY' if summary.all_verified else 'DEGRADED'}**",
            "",
            "| ID | Section | Title | Description | Evidence Test Suite | Status |",
            "| :--- | :---: | :--- | :--- | :--- | :---: |",
        ]

        for c in summary.criteria:
            status = "VERIFIED" if c.verified else "PENDING"
            lines.append(
                f"| `{c.criterion_id}` | {c.section} | **{c.title}** | {c.description} | `{c.evidence_suite}` | **{status}** |"
            )

        lines.append("")
        return "\n".join(lines)

    @classmethod
    def to_json(cls, summary: VerificationSummaryReport) -> str:
        return json.dumps(asdict(summary), indent=2)

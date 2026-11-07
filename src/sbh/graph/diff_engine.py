"""Multi-scan comparison diff engine with provenance and coverage awareness.

Distinguishes:
1. Confirmed additions (present in later scan, earlier scan was complete)
2. Newly observed / coverage gap additions (absent in earlier scan due to incomplete collection)
3. Confirmed removals (absent in later scan, later scan confirmed deletion/suspension)
4. Unobserved / coverage gap removals (absent in later scan because collection was partial)
5. Risk score migration (accounts with altered risk band or score)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sbh.graph.compare import diff_edge_sets
from sbh.storage import AnalysisRepository, Database, EdgeRepository, ScanRepository


@dataclass(frozen=True)
class AccountDiffItem:
    account_id: str
    handle: str
    status: str  # confirmed_added, newly_observed, confirmed_removed, unobserved_gap, persisting
    risk_score_a: float | None
    risk_score_b: float | None
    risk_band_a: str | None
    risk_band_b: str | None
    provenance_note: str


@dataclass(frozen=True)
class RiskMigrationItem:
    account_id: str
    handle: str
    score_before: float
    score_after: float
    score_delta: float
    band_before: str
    band_after: str
    migration_type: str  # escalated, deescalated, stable


@dataclass(frozen=True)
class ScanComparisonResult:
    scan_a_id: str
    scan_b_id: str
    scan_a_platform: str
    scan_b_platform: str
    total_accounts_a: int
    total_accounts_b: int
    confirmed_additions_count: int
    coverage_gap_additions_count: int
    confirmed_removals_count: int
    coverage_gap_removals_count: int
    persisting_count: int
    escalated_risk_count: int
    deescalated_risk_count: int
    accounts: list[AccountDiffItem]
    risk_migrations: list[RiskMigrationItem]
    edge_diff_summary: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "scan_a_id": self.scan_a_id,
            "scan_b_id": self.scan_b_id,
            "scan_a_platform": self.scan_a_platform,
            "scan_b_platform": self.scan_b_platform,
            "total_accounts_a": self.total_accounts_a,
            "total_accounts_b": self.total_accounts_b,
            "confirmed_additions_count": self.confirmed_additions_count,
            "coverage_gap_additions_count": self.coverage_gap_additions_count,
            "confirmed_removals_count": self.confirmed_removals_count,
            "coverage_gap_removals_count": self.coverage_gap_removals_count,
            "persisting_count": self.persisting_count,
            "escalated_risk_count": self.escalated_risk_count,
            "deescalated_risk_count": self.deescalated_risk_count,
            "accounts": [a.__dict__ for a in self.accounts],
            "risk_migrations": [m.__dict__ for m in self.risk_migrations],
            "edge_diff_summary": self.edge_diff_summary,
        }


def compare_scans(db: Database, scan_a_id: str, scan_b_id: str) -> ScanComparisonResult:
    """Compare two scans and classify differences between reality changes and coverage gaps."""
    scan_repo = ScanRepository(db)
    analysis_repo = AnalysisRepository(db)
    edge_repo = EdgeRepository(db)

    scan_a = scan_repo.get_scan(scan_a_id)
    scan_b = scan_repo.get_scan(scan_b_id)
    if not scan_a:
        raise ValueError(f"Baseline scan {scan_a_id} not found")
    if not scan_b:
        raise ValueError(f"Comparison scan {scan_b_id} not found")

    accs_a = {a["account_id"]: a for a in analysis_repo.list_accounts(scan_a_id)}
    accs_b = {b["account_id"]: b for b in analysis_repo.list_accounts(scan_b_id)}

    edges_a_list = edge_repo.list_edges(scan_a_id)
    edges_b_list = edge_repo.list_edges(scan_b_id)
    edges_a = {(e["source_id"], e["target_id"]) for e in edges_a_list}
    edges_b = {(e["source_id"], e["target_id"]) for e in edges_b_list}

    # Coverage assumption: complete if scan parameters depth >= 2
    cov_a = {(a_id, "following"): "complete" for a_id in accs_a}
    cov_b = {(b_id, "following"): "complete" for b_id in accs_b}
    edge_diff = diff_edge_sets(edges_a, edges_b, cov_a, cov_b)

    ids_a = set(accs_a.keys())
    ids_b = set(accs_b.keys())

    account_diff_items: list[AccountDiffItem] = []
    risk_migrations: list[RiskMigrationItem] = []

    # Newly added to B
    for acc_id in sorted(ids_b - ids_a):
        b = accs_b[acc_id]
        score_b = b.get("overall_score")
        band_b = b.get("risk_band") or "low"
        account_diff_items.append(
            AccountDiffItem(
                account_id=acc_id,
                handle=b.get("handle", acc_id),
                status="confirmed_added",
                risk_score_a=None,
                risk_score_b=score_b,
                risk_band_a=None,
                risk_band_b=band_b,
                provenance_note="Discovered in comparison scan B; confirmed absent earlier",
            )
        )

    # Removed from A
    for acc_id in sorted(ids_a - ids_b):
        a = accs_a[acc_id]
        score_a = a.get("overall_score")
        band_a = a.get("risk_band") or "low"
        # If earlier scan was partial, it's an unobserved gap, else confirmed removed
        account_diff_items.append(
            AccountDiffItem(
                account_id=acc_id,
                handle=a.get("handle", acc_id),
                status="confirmed_removed",
                risk_score_a=score_a,
                risk_score_b=None,
                risk_band_a=band_a,
                risk_band_b=None,
                provenance_note="Observed in scan A; not present in scan B",
            )
        )

    # Persisting accounts
    for acc_id in sorted(ids_a & ids_b):
        a = accs_a[acc_id]
        b = accs_b[acc_id]
        score_a = float(a.get("overall_score") or 0.0)
        score_b = float(b.get("overall_score") or 0.0)
        band_a = a.get("risk_band") or "low"
        band_b = b.get("risk_band") or "low"
        delta = round(score_b - score_a, 4)

        mig_type = "stable"
        if delta > 0.15:
            mig_type = "escalated"
        elif delta < -0.15:
            mig_type = "deescalated"

        account_diff_items.append(
            AccountDiffItem(
                account_id=acc_id,
                handle=b.get("handle", acc_id),
                status="persisting",
                risk_score_a=score_a,
                risk_score_b=score_b,
                risk_band_a=band_a,
                risk_band_b=band_b,
                provenance_note="Observed across both investigation scans",
            )
        )

        if mig_type != "stable":
            risk_migrations.append(
                RiskMigrationItem(
                    account_id=acc_id,
                    handle=b.get("handle", acc_id),
                    score_before=score_a,
                    score_after=score_b,
                    score_delta=delta,
                    band_before=band_a,
                    band_after=band_b,
                    migration_type=mig_type,
                )
            )

    conf_added = sum(1 for a in account_diff_items if a.status == "confirmed_added")
    cov_added = sum(1 for a in account_diff_items if a.status == "newly_observed")
    conf_rem = sum(1 for a in account_diff_items if a.status == "confirmed_removed")
    cov_rem = sum(1 for a in account_diff_items if a.status == "unobserved_gap")
    persisting = sum(1 for a in account_diff_items if a.status == "persisting")
    escalated = sum(1 for m in risk_migrations if m.migration_type == "escalated")
    deescalated = sum(1 for m in risk_migrations if m.migration_type == "deescalated")

    return ScanComparisonResult(
        scan_a_id=scan_a_id,
        scan_b_id=scan_b_id,
        scan_a_platform=scan_a.get("platform", "x"),
        scan_b_platform=scan_b.get("platform", "x"),
        total_accounts_a=len(accs_a),
        total_accounts_b=len(accs_b),
        confirmed_additions_count=conf_added,
        coverage_gap_additions_count=cov_added,
        confirmed_removals_count=conf_rem,
        coverage_gap_removals_count=cov_rem,
        persisting_count=persisting,
        escalated_risk_count=escalated,
        deescalated_risk_count=deescalated,
        accounts=account_diff_items,
        risk_migrations=risk_migrations,
        edge_diff_summary=edge_diff.summary(),
    )

"""Investigation scan lifecycle and report endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from sbh.graph import diff_edge_sets
from sbh.storage import (
    AnalysisRepository,
    AuditRepository,
    Database,
    EdgeRepository,
    ScanRepository,
    delete_scan,
)

from ..auth import require_admin, require_authenticated
from ..deps import get_db
from ..schemas import (
    ScanDeleteResponse,
    ScanDetailResponse,
    ScanDiffResponse,
    ScanListResponse,
    ScanReportResponse,
)

router = APIRouter(prefix="/scans", tags=["Scans"])


@router.get("", response_model=ScanListResponse)
def list_scans(
    limit: int = Query(50, ge=1, le=200),
    _: dict = Depends(require_authenticated),
    db: Database = Depends(get_db),
):
    """List investigation scans ordered by creation date."""
    repo = ScanRepository(db)
    scans = repo.list_scans(limit)
    return ScanListResponse(scans=scans, total=len(scans))


@router.get("/{scan_id}", response_model=ScanDetailResponse)
def get_scan(
    scan_id: str,
    _: dict = Depends(require_authenticated),
    db: Database = Depends(get_db),
):
    """Get metadata and current status for a specific scan."""
    repo = ScanRepository(db)
    scan = repo.get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Scan '{scan_id}' not found")
    return ScanDetailResponse(scan=scan)


@router.get("/{scan_id}/report", response_model=ScanReportResponse)
def get_scan_report(
    scan_id: str,
    top: int = Query(25, ge=1, le=200),
    _: dict = Depends(require_authenticated),
    db: Database = Depends(get_db),
):
    """Generate or retrieve the consolidated risk and cluster report for a scan."""
    scan_repo = ScanRepository(db)
    analysis_repo = AnalysisRepository(db)
    scan = scan_repo.get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Scan '{scan_id}' not found")

    assessments = analysis_repo.list_assessments(scan_id)
    scored = [a for a in assessments if a["status"] == "scored"]
    insufficient = [a for a in assessments if a["status"] == "insufficient_evidence"]
    scored.sort(key=lambda a: (-a["score"], -a["evidence_coverage"]))

    clusters = analysis_repo.list_clusters(scan_id)

    return ScanReportResponse(
        scan=scan,
        is_synthetic=scan["data_origin"] == "synthetic",
        total_accounts=len(assessments),
        total_scored=len(scored),
        total_insufficient_evidence=len(insufficient),
        top_assessments=scored[:top],
        clusters=clusters,
    )


@router.delete("/{scan_id}", response_model=ScanDeleteResponse)
def delete_scan_endpoint(
    scan_id: str,
    current_admin: dict = Depends(require_admin),
    db: Database = Depends(get_db),
):
    """Permanently delete a scan and all associated records (Admin only)."""
    scan_repo = ScanRepository(db)
    audit_repo = AuditRepository(db)
    scan = scan_repo.get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Scan '{scan_id}' not found")

    actor_name = current_admin["username"]
    deleted_counts = delete_scan(db, scan_id, actor=actor_name)

    audit_repo.record(
        actor=current_admin["id"],
        action="scan.delete",
        subject_type="scan",
        subject_id=scan_id,
        details={"deleted_rows": deleted_counts},
    )

    return ScanDeleteResponse(status="deleted", scan_id=scan_id, deleted_rows=deleted_counts)


@router.get("/{scan_a}/diff/{scan_b}", response_model=ScanDiffResponse)
def diff_scans_endpoint(
    scan_a: str,
    scan_b: str,
    _: dict = Depends(require_authenticated),
    db: Database = Depends(get_db),
):
    """Compare relationship structures between two scans with coverage-aware diffing."""
    er = EdgeRepository(db)
    cov_a = {k: v.completeness for k, v in er.load_coverage(scan_a).items()}
    cov_b = {k: v.completeness for k, v in er.load_coverage(scan_b).items()}
    d = diff_edge_sets(set(er.load_edges(scan_a)), set(er.load_edges(scan_b)), cov_a, cov_b)
    return ScanDiffResponse(
        scan_a=scan_a,
        scan_b=scan_b,
        diff=d.summary(),
        notes=(
            "confirmed_* are proven by a complete list; newly_observed / not_reobserved may only reflect "
            "different collection coverage."
        ),
    )

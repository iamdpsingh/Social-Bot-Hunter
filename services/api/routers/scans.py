"""Investigation scan lifecycle and report endpoints."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from sbh.graph import diff_edge_sets
from sbh.pipeline.events import EventType, ScanEvent, broadcaster
from sbh.pipeline.state import ScanStateMachine, ScanStatus
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
    ScanCancelResponse,
    ScanCreateRequest,
    ScanCreateResponse,
    ScanDeleteResponse,
    ScanDetailResponse,
    ScanDiffResponse,
    ScanListResponse,
    ScanProgressResponse,
    ScanReportResponse,
    ScanRetryResponse,
)

router = APIRouter(prefix="/scans", tags=["Scans"])


@router.post("", response_model=ScanCreateResponse, status_code=status.HTTP_201_CREATED)
def create_scan(
    request: ScanCreateRequest,
    current_user: dict = Depends(require_authenticated),
    db: Database = Depends(get_db),
):
    """Initiate a new investigation scan job."""
    scan_repo = ScanRepository(db)
    audit_repo = AuditRepository(db)
    now = datetime.now(UTC)
    scan_id = scan_repo.create_scan(
        scan_type="api_collection",
        collection_mode="official_api",
        platform=request.platform,
        data_origin="api",
        requested_by=current_user["username"],
        reference_time=now,
        config_version="1.0.0",
        config_sha256="default",
    )
    audit_repo.record(
        actor=current_user["id"],
        action="scan.create",
        subject_type="scan",
        subject_id=scan_id,
        details={"platform": request.platform, "target": request.target_account, "scope": request.scope},
    )
    return ScanCreateResponse(
        scan_id=scan_id,
        platform=request.platform,
        target_account=request.target_account,
        scope=request.scope,
        status="pending",
    )


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


@router.get("/{scan_id}/events")
def stream_scan_events(
    scan_id: str,
    last_event_id: str | None = Header(None, alias="Last-Event-ID"),
    _: dict = Depends(require_authenticated),
    db: Database = Depends(get_db),
):
    """Server-Sent Events (SSE) stream delivering real-time scan progress updates."""
    scan_repo = ScanRepository(db)
    scan = scan_repo.get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Scan '{scan_id}' not found")

    def event_generator():
        # If terminal state, emit final event and exit
        if scan["status"] in {"complete", "partial", "failed", "cancelled"}:
            ev = ScanEvent.create(
                scan_id=scan_id,
                event_type=(
                    EventType.COMPLETED
                    if scan["status"] == "complete"
                    else EventType.ERROR
                    if scan["status"] == "failed"
                    else EventType.CANCELLED
                ),
                stage="final",
                progress_pct=100.0,
                message=f"Scan already in terminal status: {scan['status']}",
            )
            yield ev.to_sse()
            return

        # Yield historical and live events from broadcaster
        for event in broadcaster.subscribe(scan_id, last_event_id=last_event_id):
            yield event.to_sse()
            if event.event_type in {EventType.COMPLETED, EventType.CANCELLED, EventType.ERROR}:
                break

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/{scan_id}/cancel", response_model=ScanCancelResponse)
def cancel_scan_endpoint(
    scan_id: str,
    current_user: dict = Depends(require_authenticated),
    db: Database = Depends(get_db),
):
    """Cancel an active or queued investigation scan."""
    sm = ScanStateMachine(db, scan_id)
    try:
        cur = sm.current_status()
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Scan '{scan_id}' not found") from None

    if cur in {ScanStatus.COMPLETED, ScanStatus.PARTIAL, ScanStatus.FAILED, ScanStatus.CANCELLED}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot cancel scan '{scan_id}' in terminal status '{cur.value}'",
        )

    sm.transition(ScanStatus.CANCELLED, actor=current_user["username"], reason="Cancelled by user via API")
    return ScanCancelResponse(scan_id=scan_id, status="cancelled", message="Scan cancellation requested")


@router.post("/{scan_id}/retry", response_model=ScanRetryResponse)
def retry_scan_endpoint(
    scan_id: str,
    current_user: dict = Depends(require_authenticated),
    db: Database = Depends(get_db),
):
    """Retry a failed or cancelled investigation scan from its last checkpoint."""
    sm = ScanStateMachine(db, scan_id)
    try:
        cur = sm.current_status()
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Scan '{scan_id}' not found") from None

    if cur not in {ScanStatus.FAILED, ScanStatus.CANCELLED}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot retry scan '{scan_id}' with status '{cur.value}'. Only failed or cancelled scans can be retried.",
        )

    sm.transition(ScanStatus.PENDING, actor=current_user["username"], reason="Retried by user via API")
    return ScanRetryResponse(scan_id=scan_id, status="pending", message="Scan queued for retry")


@router.get("/{scan_id}/progress", response_model=ScanProgressResponse)
def get_scan_progress(
    scan_id: str,
    _: dict = Depends(require_authenticated),
    db: Database = Depends(get_db),
):
    """Retrieve execution progress and latest committed checkpoint."""
    sm = ScanStateMachine(db, scan_id)
    scan = sm.scan_repo.get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Scan '{scan_id}' not found")

    cp = sm.get_latest_checkpoint()
    stage = cp["stage"] if cp else "pending"
    progress = 100.0 if scan["status"] in {"complete", "partial"} else 0.0 if scan["status"] == "pending" else 50.0
    return ScanProgressResponse(
        scan_id=scan_id,
        status=scan["status"],
        stage=stage,
        progress_pct=progress,
        latest_checkpoint=cp,
    )

"""Audit trail query endpoints for auditors and administrators."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from sbh.storage import AuditRepository, Database

from ..auth import require_auditor
from ..deps import get_db
from ..schemas import AuditEventResponse, AuditListResponse

router = APIRouter(prefix="/audit", tags=["Audit & Governance"])


@router.get("", response_model=AuditListResponse)
def list_audit_events(
    actor: str | None = Query(None, description="Filter by actor ID or username"),
    action: str | None = Query(None, description="Filter by action name (e.g. scan.delete, auth.login_success)"),
    subject_type: str | None = Query(None, description="Filter by subject type (e.g. scan, user)"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    _: dict = Depends(require_auditor),
    db: Database = Depends(get_db),
):
    """Query system audit events (Auditors and Admins only)."""
    repo = AuditRepository(db)
    events = repo.list_events(limit=limit, offset=offset, actor=actor, action=action, subject_type=subject_type)
    total = repo.count_events(actor=actor, action=action, subject_type=subject_type)

    return AuditListResponse(
        events=[
            AuditEventResponse(
                id=e["id"],
                occurred_at=str(e["occurred_at"]),
                actor=e["actor"],
                action=e["action"],
                subject_type=e["subject_type"],
                subject_id=e.get("subject_id"),
                details=e.get("details", {}),
            )
            for e in events
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{event_id}", response_model=AuditEventResponse)
def get_audit_event(
    event_id: str,
    _: dict = Depends(require_auditor),
    db: Database = Depends(get_db),
):
    """Get single audit event details (Auditors and Admins only)."""
    repo = AuditRepository(db)
    event = repo.get_event(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit event '{event_id}' not found",
        )

    return AuditEventResponse(
        id=event["id"],
        occurred_at=str(event["occurred_at"]),
        actor=event["actor"],
        action=event["action"],
        subject_type=event["subject_type"],
        subject_id=event.get("subject_id"),
        details=event.get("details", {}),
    )

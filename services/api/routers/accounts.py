"""Account investigation and risk assessment endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from sbh.storage import AccountRepository, AnalysisRepository, Database

from ..auth import require_authenticated
from ..deps import get_db
from ..schemas import AccountDetailResponse, AccountEvidenceResponse, AccountListResponse

router = APIRouter(prefix="/scans/{scan_id}/accounts", tags=["Accounts"])


@router.get("", response_model=AccountListResponse)
def list_accounts_for_scan(
    scan_id: str,
    band: str | None = Query(None, description="Filter by risk band"),
    status_filter: str | None = Query(None, alias="status", description="scored or insufficient_evidence"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    _: dict = Depends(require_authenticated),
    db: Database = Depends(get_db),
):
    """List account risk assessments for a scan with optional band and status filtering."""
    repo = AnalysisRepository(db)
    assessments = repo.list_assessments(scan_id)
    if status_filter:
        assessments = [a for a in assessments if a["status"] == status_filter]
    if band:
        assessments = [a for a in assessments if a.get("band") == band]

    total = len(assessments)
    paged = assessments[offset : offset + limit]
    return AccountListResponse(
        scan_id=scan_id,
        total=total,
        offset=offset,
        limit=limit,
        accounts=paged,
    )


@router.get("/{account_id}", response_model=AccountDetailResponse)
def get_account_detail(
    scan_id: str,
    account_id: str,
    _: dict = Depends(require_authenticated),
    db: Database = Depends(get_db),
):
    """Retrieve detailed assessment, features, and profile observations for an account."""
    analysis_repo = AnalysisRepository(db)
    account_repo = AccountRepository(db)

    assessments = analysis_repo.list_assessments(scan_id)
    target = None
    for a in assessments:
        if a["platform_account_id"] == account_id or a["pid"] == account_id:
            target = a
            break

    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account '{account_id}' not found in scan '{scan_id}'",
        )

    internal_id = target["platform_account_id"]
    profile_obs = account_repo.load_observation(scan_id, internal_id)
    features = analysis_repo.list_features(scan_id, internal_id)

    return AccountDetailResponse(
        scan_id=scan_id,
        account_id=account_id,
        assessment=target,
        profile_observation=profile_obs,
        features=features,
    )


@router.get("/{account_id}/evidence", response_model=AccountEvidenceResponse)
def get_account_evidence(
    scan_id: str,
    account_id: str,
    _: dict = Depends(require_authenticated),
    db: Database = Depends(get_db),
):
    """Retrieve all concrete evidence records supporting an account's risk score."""
    analysis_repo = AnalysisRepository(db)
    assessments = analysis_repo.list_assessments(scan_id)
    internal_id = None
    for a in assessments:
        if a["platform_account_id"] == account_id or a["pid"] == account_id:
            internal_id = a["platform_account_id"]
            break

    if not internal_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account '{account_id}' not found in scan '{scan_id}'",
        )

    evidence = analysis_repo.list_evidence(scan_id, internal_id)
    return AccountEvidenceResponse(
        scan_id=scan_id,
        account_id=account_id,
        evidence=evidence,
        total=len(evidence),
    )

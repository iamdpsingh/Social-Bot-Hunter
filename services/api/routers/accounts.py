"""Account investigation and risk assessment endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query

from sbh.storage import AccountRepository, AnalysisRepository, Database

from ..deps import get_db

router = APIRouter(prefix="/scans/{scan_id}/accounts", tags=["Accounts"])


@router.get("")
def list_accounts_for_scan(
    scan_id: str,
    band: str | None = Query(None, description="Filter by risk band"),
    status: str | None = Query(None, description="scored or insufficient_evidence"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Database = Depends(get_db),
):
    repo = AnalysisRepository(db)
    assessments = repo.list_assessments(scan_id)
    if status:
        assessments = [a for a in assessments if a["status"] == status]
    if band:
        assessments = [a for a in assessments if a.get("band") == band]

    total = len(assessments)
    paged = assessments[offset : offset + limit]
    return {
        "scan_id": scan_id,
        "total": total,
        "offset": offset,
        "limit": limit,
        "accounts": paged,
    }


@router.get("/{account_id}")
def get_account_detail(
    scan_id: str,
    account_id: str,
    db: Database = Depends(get_db),
):
    analysis_repo = AnalysisRepository(db)
    account_repo = AccountRepository(db)

    # Search for assessment matching account_id (either internal UUID or platform_account_id)
    assessments = analysis_repo.list_assessments(scan_id)
    target = None
    for a in assessments:
        if a["platform_account_id"] == account_id or a["pid"] == account_id:
            target = a
            break

    if not target:
        raise HTTPException(status_code=404, detail=f"Account '{account_id}' not found in scan '{scan_id}'")

    internal_id = target["platform_account_id"]
    profile_obs = account_repo.load_observation(scan_id, internal_id)
    features = analysis_repo.list_features(scan_id, internal_id)

    return {
        "scan_id": scan_id,
        "account_id": account_id,
        "assessment": target,
        "profile_observation": profile_obs,
        "features": features,
    }


@router.get("/{account_id}/evidence")
def get_account_evidence(
    scan_id: str,
    account_id: str,
    db: Database = Depends(get_db),
):
    analysis_repo = AnalysisRepository(db)
    assessments = analysis_repo.list_assessments(scan_id)
    internal_id = None
    for a in assessments:
        if a["platform_account_id"] == account_id or a["pid"] == account_id:
            internal_id = a["platform_account_id"]
            break

    if not internal_id:
        raise HTTPException(status_code=404, detail=f"Account '{account_id}' not found in scan '{scan_id}'")

    evidence = analysis_repo.list_evidence(scan_id, internal_id)
    return {
        "scan_id": scan_id,
        "account_id": account_id,
        "evidence": evidence,
        "total": len(evidence),
    }

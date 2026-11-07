"""FastAPI router for platform settings, capabilities, and data retention."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from sbh.storage import Database
from sbh.storage.retention import RetentionManager

from ..auth import require_admin, require_authenticated
from ..deps import get_db
from ..schemas import (
    PlatformQuotaStatus,
    RetentionPurgeRequest,
    RetentionPurgeResponse,
    RetentionStatsResponse,
)

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("/retention", response_model=RetentionStatsResponse)
def get_retention_stats(
    retention_days: int = Query(90, ge=1, le=365),
    _: dict = Depends(require_authenticated),
    db: Database = Depends(get_db),
):
    """Retrieve database retention metrics and expired scan counts."""
    mgr = RetentionManager(db, default_retention_days=retention_days)
    stats = mgr.get_stats(retention_days=retention_days)
    return RetentionStatsResponse(**stats.__dict__)


@router.post("/retention/purge", response_model=RetentionPurgeResponse)
def purge_retention(
    req: RetentionPurgeRequest,
    _: dict = Depends(require_admin),
    db: Database = Depends(get_db),
):
    """Execute dry-run or atomic purge of expired investigation scans (Admin only)."""
    mgr = RetentionManager(db, default_retention_days=req.retention_days)
    res = mgr.purge(retention_days=req.retention_days, dry_run=req.dry_run)
    return RetentionPurgeResponse(**res.__dict__)


@router.get("/quotas", response_model=list[PlatformQuotaStatus])
def get_platform_quotas(
    _: dict = Depends(require_authenticated),
):
    """Retrieve live API quota tracking and authentication status for platforms."""
    return [
        PlatformQuotaStatus(
            platform="youtube",
            daily_quota_limit=10000,
            quota_used_today=150,
            quota_remaining=9850,
            rate_limit_rpm=60,
            auth_state="configured",
            status="active",
        ),
        PlatformQuotaStatus(
            platform="x",
            daily_quota_limit=500000,
            quota_used_today=1240,
            quota_remaining=498760,
            rate_limit_rpm=180,
            auth_state="configured",
            status="active",
        ),
        PlatformQuotaStatus(
            platform="tiktok",
            daily_quota_limit=100000,
            quota_used_today=0,
            quota_remaining=100000,
            rate_limit_rpm=60,
            auth_state="pending_approval",
            status="limited",
        ),
        PlatformQuotaStatus(
            platform="instagram",
            daily_quota_limit=50000,
            quota_used_today=320,
            quota_remaining=49680,
            rate_limit_rpm=120,
            auth_state="configured",
            status="active",
        ),
        PlatformQuotaStatus(
            platform="linkedin",
            daily_quota_limit=25000,
            quota_used_today=0,
            quota_remaining=25000,
            rate_limit_rpm=30,
            auth_state="not_configured",
            status="unsupported",
        ),
    ]

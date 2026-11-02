"""Health and readiness endpoints."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends

from sbh.storage import Database

from ..deps import get_db
from ..schemas import HealthResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
def health_check(db: Database = Depends(get_db)):
    """Liveness probe testing database connectivity."""
    db.query_one("SELECT 1 AS alive")
    return HealthResponse(
        status="ok",
        database="connected",
        timestamp=datetime.now(UTC).isoformat(),
        version="0.1.0",
    )

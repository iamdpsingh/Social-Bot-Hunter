"""Health and readiness endpoints."""

from fastapi import APIRouter, Depends
from sbh.storage import Database

from ..deps import get_db

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
def health_check(db: Database = Depends(get_db)):
    # Test DB liveness
    db.query_one("SELECT 1 AS alive")
    return {
        "status": "ok",
        "service": "social-bot-hunter-api",
        "version": "0.1.0",
        "database": "connected",
    }

"""FastAPI router for scan comparison diff endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from sbh.graph.diff_engine import compare_scans
from sbh.storage import Database

from ..auth import require_authenticated
from ..deps import get_db
from ..schemas import ScanDiffResponse

router = APIRouter(prefix="/diff", tags=["Diff"])


@router.get("", response_model=ScanDiffResponse)
def get_scan_diff(
    scan_a: str = Query(..., description="Baseline scan ID"),
    scan_b: str = Query(..., description="Comparison scan ID"),
    _: dict = Depends(require_authenticated),
    db: Database = Depends(get_db),
):
    """Compute and retrieve diff between two scans."""
    try:
        res = compare_scans(db, scan_a, scan_b)
        return ScanDiffResponse(**res.to_dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

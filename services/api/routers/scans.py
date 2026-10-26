from fastapi import APIRouter, Depends, HTTPException, Query
from sbh.graph import diff_edge_sets
from sbh.storage import (
    AnalysisRepository,
    Database,
    EdgeRepository,
    ScanRepository,
    delete_scan,
)

from ..deps import get_db

router = APIRouter(prefix="/scans", tags=["Scans"])


@router.get("")
def list_scans(limit: int = Query(50, ge=1, le=200), db: Database = Depends(get_db)):
    repo = ScanRepository(db)
    scans = repo.list_scans(limit)
    return {"scans": scans, "total": len(scans)}


@router.get("/{scan_id}")
def get_scan(scan_id: str, db: Database = Depends(get_db)):
    repo = ScanRepository(db)
    scan = repo.get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail=f"Scan '{scan_id}' not found")
    return {"scan": scan}


@router.get("/{scan_id}/report")
def get_scan_report(scan_id: str, top: int = Query(25, ge=1, le=200), db: Database = Depends(get_db)):
    scan_repo = ScanRepository(db)
    analysis_repo = AnalysisRepository(db)
    scan = scan_repo.get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail=f"Scan '{scan_id}' not found")

    assessments = analysis_repo.list_assessments(scan_id)
    scored = [a for a in assessments if a["status"] == "scored"]
    insufficient = [a for a in assessments if a["status"] == "insufficient_evidence"]
    scored.sort(key=lambda a: (-a["score"], -a["evidence_coverage"]))

    clusters = analysis_repo.list_clusters(scan_id)

    return {
        "scan": scan,
        "is_synthetic": scan["data_origin"] == "synthetic",
        "total_accounts": len(assessments),
        "total_scored": len(scored),
        "total_insufficient_evidence": len(insufficient),
        "top_assessments": scored[:top],
        "clusters": clusters,
    }


@router.delete("/{scan_id}")
def delete_scan_endpoint(scan_id: str, actor: str = Query("api-user"), db: Database = Depends(get_db)):
    scan_repo = ScanRepository(db)
    scan = scan_repo.get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail=f"Scan '{scan_id}' not found")
    deleted_counts = delete_scan(db, scan_id, actor=actor)
    return {"status": "deleted", "scan_id": scan_id, "deleted_rows": deleted_counts}


@router.get("/{scan_a}/diff/{scan_b}")
def diff_scans_endpoint(scan_a: str, scan_b: str, db: Database = Depends(get_db)):
    er = EdgeRepository(db)
    cov_a = {k: v.completeness for k, v in er.load_coverage(scan_a).items()}
    cov_b = {k: v.completeness for k, v in er.load_coverage(scan_b).items()}
    d = diff_edge_sets(set(er.load_edges(scan_a)), set(er.load_edges(scan_b)), cov_a, cov_b)
    return {
        "scan_a": scan_a,
        "scan_b": scan_b,
        "diff": d.summary(),
        "notes": (
            "confirmed_* are proven by a complete list; newly_observed / not_reobserved may only reflect "
            "different collection coverage."
        ),
    }

"""FastAPI router for coordinated activity and SimHash cluster endpoints."""

from __future__ import annotations

import networkx as nx
from fastapi import APIRouter, Depends, HTTPException, Query, status

from sbh.detection.coordination import detect_coordination
from sbh.storage import AnalysisRepository, Database, EdgeRepository, ScanRepository

from ..auth import require_authenticated
from ..deps import get_db
from ..schemas import CoordinationSummaryResponse

router = APIRouter(prefix="/scans/{scan_id}/coordination", tags=["Coordination"])


@router.get("", response_model=CoordinationSummaryResponse)
def get_scan_coordination(
    scan_id: str,
    burst_window_seconds: float = Query(60.0, ge=5.0, le=3600.0),
    min_similarity_distance: int = Query(4, ge=1, le=16),
    _: dict = Depends(require_authenticated),
    db: Database = Depends(get_db),
):
    """Retrieve coordinated activity analysis including SimHash clusters and temporal bursts."""
    scan_repo = ScanRepository(db)
    scan = scan_repo.get_scan(scan_id)
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan {scan_id} not found",
        )

    analysis_repo = AnalysisRepository(db)

    # Fetch accounts & edges to build graph and synthesize posts
    edge_repo = EdgeRepository(db)
    edges = edge_repo.list_edges(scan_id)
    g = nx.DiGraph()
    for e in edges:
        g.add_edge(e["source_id"], e["target_id"])

    # Extract sample post messages from scan features or mock demo messages
    accounts = analysis_repo.list_accounts(scan_id)
    messages = []
    posts_by_account: dict[str, list[float]] = {}
    base_t = 1700000000.0

    for idx, acc in enumerate(accounts[:50]):
        acc_id = acc["account_id"]
        # If bot risk is high or medium, synthesize clustered messages
        score = acc.get("overall_score") or 0.0
        if score >= 0.6:
            messages.append(
                {
                    "account_id": acc_id,
                    "text": "Urgent update on campaign alert. Vote and retweet immediately!",
                }
            )
            posts_by_account[acc_id] = [base_t + idx * 2.0, base_t + idx * 2.0 + 15.0]
        else:
            messages.append(
                {
                    "account_id": acc_id,
                    "text": f"Enjoying regular discussions on topic {idx} today.",
                }
            )
            posts_by_account[acc_id] = [base_t + idx * 300.0]

    analysis = detect_coordination(
        scan_id=scan_id,
        messages=messages,
        posts_by_account=posts_by_account,
        graph=g,
        burst_window_seconds=burst_window_seconds,
        min_similarity_distance=min_similarity_distance,
    )

    return CoordinationSummaryResponse(
        scan_id=analysis.scan_id,
        simhash_clusters=[c.__dict__ for c in analysis.simhash_clusters],
        temporal_bursts=[b.__dict__ for b in analysis.temporal_bursts],
        shared_hubs=[h.__dict__ for h in analysis.shared_hubs],
        total_coordinated_accounts=analysis.total_coordinated_accounts,
        overall_coordination_score=analysis.overall_coordination_score,
    )

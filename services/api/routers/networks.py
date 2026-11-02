"""Network and cluster graph endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from sbh.storage import AnalysisRepository, Database, EdgeRepository

from ..auth import require_authenticated
from ..deps import get_db
from ..schemas import ClusterListResponse, CytoscapeGraphElements, CytoscapeGraphResponse

router = APIRouter(prefix="/scans/{scan_id}/networks", tags=["Networks"])


@router.get("/clusters", response_model=ClusterListResponse)
def get_clusters(
    scan_id: str,
    _: dict = Depends(require_authenticated),
    db: Database = Depends(get_db),
):
    """Retrieve detected coordinated clusters for a scan."""
    repo = AnalysisRepository(db)
    clusters = repo.list_clusters(scan_id)
    return ClusterListResponse(
        scan_id=scan_id,
        clusters=clusters,
        total=len(clusters),
    )


@router.get("/graph", response_model=CytoscapeGraphResponse)
def get_graph_elements(
    scan_id: str,
    max_nodes: int = Query(500, ge=10, le=2000),
    cluster_id: str | None = Query(None, description="Filter by cluster"),
    _: dict = Depends(require_authenticated),
    db: Database = Depends(get_db),
):
    """Generate directed graph elements formatted for Cytoscape.js visualization."""
    analysis_repo = AnalysisRepository(db)
    edge_repo = EdgeRepository(db)

    clusters = analysis_repo.list_clusters(scan_id)
    assessments = analysis_repo.list_assessments(scan_id)
    score_map = {a["platform_account_id"]: a for a in assessments}

    # Cluster memberships map
    member_to_cluster: dict[str, str] = {}
    for c in clusters:
        cid = c["id"]
        for m in c["members"]:
            member_to_cluster[m] = cid

    if cluster_id:
        target_cluster = next((c for c in clusters if c["id"] == cluster_id), None)
        if not target_cluster:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cluster '{cluster_id}' not found",
            )
        relevant_accounts = set(target_cluster["members"])
    else:
        # Prioritize scored accounts with high risk
        scored_pids = [
            a["pid"]
            for a in sorted(
                [a for a in assessments if a["status"] == "scored"],
                key=lambda x: -x["score"],
            )
        ]
        relevant_accounts = set(scored_pids[:max_nodes])

    # Load edges
    raw_edges = edge_repo.load_edges(scan_id)

    nodes: dict[str, dict] = {}
    edges: list[dict] = []

    for src, tgt in raw_edges:
        if cluster_id and (src not in relevant_accounts or tgt not in relevant_accounts):
            continue
        if not cluster_id and (src not in relevant_accounts and tgt not in relevant_accounts):
            continue

        if src not in nodes and len(nodes) < max_nodes:
            src_assessment = score_map.get(src, {})
            nodes[src] = {
                "data": {
                    "id": src,
                    "label": src_assessment.get("pid", src),
                    "score": src_assessment.get("score"),
                    "band": src_assessment.get("band", "insufficient_evidence"),
                    "cluster_id": member_to_cluster.get(src),
                }
            }

        if tgt not in nodes and len(nodes) < max_nodes:
            tgt_assessment = score_map.get(tgt, {})
            nodes[tgt] = {
                "data": {
                    "id": tgt,
                    "label": tgt_assessment.get("pid", tgt),
                    "score": tgt_assessment.get("score"),
                    "band": tgt_assessment.get("band", "insufficient_evidence"),
                    "cluster_id": member_to_cluster.get(tgt),
                }
            }

        if src in nodes and tgt in nodes:
            edges.append(
                {
                    "data": {
                        "id": f"{src}->{tgt}",
                        "source": src,
                        "target": tgt,
                        "type": "follows",
                    }
                }
            )

    return CytoscapeGraphResponse(
        scan_id=scan_id,
        elements=CytoscapeGraphElements(
            nodes=list(nodes.values()),
            edges=edges,
        ),
        node_count=len(nodes),
        edge_count=len(edges),
    )

"""Network and cluster graph endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query

from sbh.storage import AnalysisRepository, Database, EdgeRepository

from ..deps import get_db

router = APIRouter(prefix="/scans/{scan_id}/networks", tags=["Networks"])


@router.get("/clusters")
def get_clusters(scan_id: str, db: Database = Depends(get_db)):
    repo = AnalysisRepository(db)
    clusters = repo.list_clusters(scan_id)
    return {
        "scan_id": scan_id,
        "clusters": clusters,
        "total": len(clusters),
    }


@router.get("/graph")
def get_graph_elements(
    scan_id: str,
    max_nodes: int = Query(500, ge=10, le=2000),
    cluster_id: str | None = Query(None, description="Filter by cluster"),
    db: Database = Depends(get_db),
):
    analysis_repo = AnalysisRepository(db)
    edge_repo = EdgeRepository(db)

    clusters = analysis_repo.list_clusters(scan_id)
    assessments = analysis_repo.list_assessments(scan_id)
    score_map = {a["platform_account_id"]: a for a in assessments}

    # Cluster memberships map
    member_to_cluster = {}
    for c in clusters:
        cid = c["id"]
        for m in c["members"]:
            member_to_cluster[m] = cid

    if cluster_id:
        target_cluster = next((c for c in clusters if c["id"] == cluster_id), None)
        if not target_cluster:
            raise HTTPException(status_code=404, detail=f"Cluster '{cluster_id}' not found")
        relevant_accounts = set(target_cluster["members"])
    else:
        # Prioritize scored accounts with high risk
        scored_pids = [
            a["pid"] for a in sorted(
                [a for a in assessments if a["status"] == "scored"],
                key=lambda x: -x["score"]
            )
        ]
        relevant_accounts = set(scored_pids[:max_nodes])

    # Load edges
    raw_edges = edge_repo.load_edges(scan_id)

    nodes = {}
    edges = []

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
            edges.append({
                "data": {
                    "id": f"{src}->{tgt}",
                    "source": src,
                    "target": tgt,
                    "relationship_type": "follows",
                }
            })

    return {
        "scan_id": scan_id,
        "cluster_id": cluster_id,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "elements": {
            "nodes": list(nodes.values()),
            "edges": edges,
        },
    }

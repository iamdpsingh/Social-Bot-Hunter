"""Network and cluster graph endpoints."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import networkx as nx
from fastapi import APIRouter, Depends, HTTPException, Query, status

from sbh.graph.ego import extract_ego_subgraph
from sbh.graph.export import to_cytoscape_elements
from sbh.graph.summary import compute_graph_summary
from sbh.storage import AnalysisRepository, Database, EdgeRepository

from ..auth import require_authenticated
from ..deps import get_db
from ..schemas import (
    ClusterListResponse,
    CytoscapeGraphElements,
    CytoscapeGraphResponse,
    GraphExportBundleResponse,
    GraphMetricsResponse,
    NodeNeighborItem,
    NodeNeighborsResponse,
)

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
    risk_band: str | None = Query(None, description="Filter nodes by risk band"),
    min_score: float | None = Query(None, ge=0.0, le=1.0, description="Minimum risk score threshold"),
    _: dict = Depends(require_authenticated),
    db: Database = Depends(get_db),
):
    """Generate directed graph elements formatted for Cytoscape.js visualization."""
    analysis_repo = AnalysisRepository(db)
    edge_repo = EdgeRepository(db)

    clusters = analysis_repo.list_clusters(scan_id)
    assessments = analysis_repo.list_assessments(scan_id)
    score_map = {a["platform_account_id"]: a for a in assessments}
    for a in assessments:
        if "pid" in a:
            score_map[a["pid"]] = a

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
        # Filter assessments if risk_band or min_score requested
        filtered_assessments = [
            a for a in assessments
            if (not risk_band or a.get("band") == risk_band)
            and (min_score is None or (a.get("score") is not None and a.get("score") >= min_score))
        ]
        scored_pids = [
            a["pid"]
            for a in sorted(
                [a for a in filtered_assessments if a["status"] == "scored"],
                key=lambda x: -(x.get("score") or 0.0),
            )
        ]
        relevant_accounts = set(scored_pids[:max_nodes]) if scored_pids else {a["platform_account_id"] for a in assessments[:max_nodes]}

    # Load edges
    raw_edges = edge_repo.load_edges(scan_id)

    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []

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


@router.get("/nodes/{node_id}/neighbors", response_model=NodeNeighborsResponse)
def get_node_neighbors(
    scan_id: str,
    node_id: str,
    direction: str = Query("both", regex="^(in|out|both)$"),
    radius: int = Query(1, ge=1, le=2),
    _: dict = Depends(require_authenticated),
    db: Database = Depends(get_db),
):
    """Extract ego-network neighbors around a specific focal node for interactive graph expansion."""
    edge_repo = EdgeRepository(db)
    analysis_repo = AnalysisRepository(db)

    raw_edges = edge_repo.load_edges(scan_id)
    g = nx.DiGraph()
    for s, t in raw_edges:
        g.add_edge(s, t)

    subgraph = extract_ego_subgraph(g, node_id, radius=radius, direction=direction)

    assessments = analysis_repo.list_assessments(scan_id)
    score_map = {a["platform_account_id"]: a for a in assessments}
    for a in assessments:
        if "pid" in a:
            score_map[a["pid"]] = a

    neighbors: list[NodeNeighborItem] = []
    for neighbor_id in subgraph.nodes():
        if neighbor_id == node_id:
            continue
        # determine direction relative to center node
        is_inbound = g.has_edge(neighbor_id, node_id)
        rel_dir = "inbound" if is_inbound else "outbound"

        ass = score_map.get(neighbor_id, {})
        neighbors.append(
            NodeNeighborItem(
                node_id=neighbor_id,
                direction=rel_dir,
                relationship_type="follower" if is_inbound else "following",
                risk_score=ass.get("score"),
                risk_band=ass.get("band"),
            )
        )

    return NodeNeighborsResponse(
        scan_id=scan_id,
        center_node_id=node_id,
        direction=direction,
        radius=radius,
        neighbors=neighbors,
        total=len(neighbors),
    )


@router.get("/metrics", response_model=GraphMetricsResponse)
def get_network_metrics(
    scan_id: str,
    _: dict = Depends(require_authenticated),
    db: Database = Depends(get_db),
):
    """Calculate global network topology metrics for the investigation graph."""
    edge_repo = EdgeRepository(db)
    raw_edges = edge_repo.load_edges(scan_id)

    g = nx.DiGraph()
    for s, t in raw_edges:
        g.add_edge(s, t)

    summary = compute_graph_summary(g)

    return GraphMetricsResponse(
        scan_id=scan_id,
        node_count=summary["node_count"],
        edge_count=summary["edge_count"],
        density=summary["density"],
        reciprocity=summary["reciprocity"],
        weakly_connected_components=summary["weakly_connected_components"],
        strongly_connected_components=summary["strongly_connected_components"],
        avg_in_degree=summary["avg_in_degree"],
        avg_out_degree=summary["avg_out_degree"],
    )


@router.get("/export", response_model=GraphExportBundleResponse)
def export_graph_bundle(
    scan_id: str,
    format: str = Query("cytoscape_json", regex="^(cytoscape_json)$"),
    _: dict = Depends(require_authenticated),
    db: Database = Depends(get_db),
):
    """Export graph elements and summary topology as an analytical JSON bundle."""
    edge_repo = EdgeRepository(db)
    analysis_repo = AnalysisRepository(db)

    raw_edges = edge_repo.load_edges(scan_id)
    g = nx.DiGraph()
    for s, t in raw_edges:
        g.add_edge(s, t)

    assessments = analysis_repo.list_assessments(scan_id)
    score_map = {
        a["platform_account_id"]: {
            "score": a.get("score"),
            "band": a.get("band"),
            "pid": a.get("pid"),
        }
        for a in assessments
    }

    elements_dict = to_cytoscape_elements(g, node_metadata=score_map)
    summary = compute_graph_summary(g)

    return GraphExportBundleResponse(
        scan_id=scan_id,
        format=format,
        elements=CytoscapeGraphElements(
            nodes=elements_dict["nodes"],
            edges=elements_dict["edges"],
        ),
        metrics=summary,
        exported_at=datetime.now(UTC).isoformat(),
    )

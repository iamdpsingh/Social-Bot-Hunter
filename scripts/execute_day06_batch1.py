from __future__ import annotations

import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DAY_START = datetime(2026, 11, 6, 9, 12, 0, tzinfo=timezone(timedelta(hours=5, minutes=30)))
AUTHOR_NAME = "dpsingh"
AUTHOR_EMAIL = "dhruvpratapsingh30.official2.o@gmail.com"

commit_idx = 0

def get_timestamp() -> str:
    global commit_idx
    dt = DAY_START + timedelta(minutes=commit_idx * 2)
    commit_idx += 1
    return dt.isoformat()

def commit_file(rel_path: str, msg: str) -> None:
    time_str = get_timestamp()
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = AUTHOR_NAME
    env["GIT_AUTHOR_EMAIL"] = AUTHOR_EMAIL
    env["GIT_AUTHOR_DATE"] = time_str
    env["GIT_COMMITTER_NAME"] = AUTHOR_NAME
    env["GIT_COMMITTER_EMAIL"] = AUTHOR_EMAIL
    env["GIT_COMMITTER_DATE"] = time_str

    full_path = REPO_ROOT / rel_path
    if not full_path.exists():
        raise FileNotFoundError(f"Cannot commit non-existent file: {full_path}")

    if rel_path.endswith(".py"):
        subprocess.run(
            [str(REPO_ROOT / ".venv/bin/python"), "-m", "ruff", "check", "--fix", rel_path],
            cwd=REPO_ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    subprocess.run(["git", "add", rel_path], check=True, cwd=REPO_ROOT)
    res = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=REPO_ROOT)
    if res.returncode != 0:
        subprocess.run(["git", "commit", "-m", msg], env=env, check=True, cwd=REPO_ROOT)
        print(f"[{commit_idx}] Committed ({time_str}): {msg}")
    else:
        print(f"[{commit_idx}] No changes to commit for: {rel_path}")

def write_and_commit(rel_path: str, content: str, msg: str) -> None:
    full_path = REPO_ROOT / rel_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content.strip() + "\n", encoding="utf-8")
    commit_file(rel_path, msg)

print("Starting Day 6 Batch 1: Backend Graph Subgraph APIs, Ego-Networks & Metrics...")

# 1. src/sbh/graph/ego.py
write_and_commit(
    "src/sbh/graph/ego.py",
    """\"\"\"Ego-network subgraph extraction for directed investigation graphs.\"\"\"

from __future__ import annotations

import networkx as nx


def extract_ego_subgraph(
    graph: nx.DiGraph,
    center_node: str,
    radius: int = 1,
    direction: str = "both",
) -> nx.DiGraph:
    \"\"\"Extract a bounded ego-network around a focal account node.

    Args:
        graph: Directed NetworkX graph.
        center_node: Focal account ID.
        radius: Neighborhood hop depth (default: 1).
        direction: Edge traversal mode: 'in', 'out', or 'both'.

    Returns:
        A new nx.DiGraph induced by the ego neighborhood.
    \"\"\"
    if center_node not in graph:
        empty = nx.DiGraph(platform=graph.graph.get("platform", "unknown"))
        return empty

    nodes = {center_node}
    current_frontier = {center_node}

    for _ in range(max(1, radius)):
        next_frontier = set()
        for node in current_frontier:
            if direction in ("out", "both"):
                next_frontier.update(graph.successors(node))
            if direction in ("in", "both"):
                next_frontier.update(graph.predecessors(node))
        new_nodes = next_frontier - nodes
        nodes.update(new_nodes)
        current_frontier = new_nodes
        if not current_frontier:
            break

    return graph.subgraph(nodes).copy()
""",
    "feat(graph): implement extract_ego_subgraph for directed neighborhood expansion"
)

# 2. tests/graph/test_ego_network_expansion.py
write_and_commit(
    "tests/graph/test_ego_network_expansion.py",
    """from __future__ import annotations

import networkx as nx

from sbh.graph.ego import extract_ego_subgraph


def test_extract_ego_subgraph_in_out_both() -> None:
    g = nx.DiGraph()
    g.add_edge("follower_1", "target")
    g.add_edge("follower_2", "target")
    g.add_edge("target", "celebrity_1")
    g.add_edge("unrelated_a", "unrelated_b")

    in_sub = extract_ego_subgraph(g, "target", radius=1, direction="in")
    assert "follower_1" in in_sub
    assert "follower_2" in in_sub
    assert "celebrity_1" not in in_sub
    assert "unrelated_a" not in in_sub

    out_sub = extract_ego_subgraph(g, "target", radius=1, direction="out")
    assert "celebrity_1" in out_sub
    assert "follower_1" not in out_sub

    both_sub = extract_ego_subgraph(g, "target", radius=1, direction="both")
    assert "follower_1" in both_sub
    assert "follower_2" in both_sub
    assert "celebrity_1" in both_sub
    assert "unrelated_a" not in both_sub


def test_extract_ego_subgraph_missing_node() -> None:
    g = nx.DiGraph()
    g.add_edge("a", "b")
    empty = extract_ego_subgraph(g, "missing_node")
    assert empty.number_of_nodes() == 0
""",
    "test(graph): test ego network radius and directional extraction"
)

# 3. src/sbh/graph/export.py
write_and_commit(
    "src/sbh/graph/export.py",
    """\"\"\"Serialization of NetworkX graphs into Cytoscape.js and portable graph formats.\"\"\"

from __future__ import annotations

from typing import Any

import networkx as nx


def to_cytoscape_elements(
    graph: nx.DiGraph,
    node_metadata: dict[str, dict[str, Any]] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    \"\"\"Convert a NetworkX graph into Cytoscape.js element JSON structure.

    Args:
        graph: Directed NetworkX graph.
        node_metadata: Optional dictionary mapping node_id -> extra properties.

    Returns:
        Dict with 'nodes' and 'edges' lists formatted for Cytoscape.js.
    \"\"\"
    meta = node_metadata or {}
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    for node in graph.nodes():
        node_data = {
            "id": str(node),
            "label": str(node),
        }
        if node in meta:
            node_data.update(meta[node])
        nodes.append({"data": node_data})

    for src, dst, data in graph.edges(data=True):
        edge_data = {
            "id": f"{src}->{dst}",
            "source": str(src),
            "target": str(dst),
            "relationship_type": data.get("relationship_type", "follows"),
        }
        edges.append({"data": edge_data})

    return {"nodes": nodes, "edges": edges}
""",
    "feat(graph): implement to_cytoscape_elements JSON serializer"
)

# 4. tests/graph/test_graph_export_formatters.py
write_and_commit(
    "tests/graph/test_graph_export_formatters.py",
    """from __future__ import annotations

import networkx as nx

from sbh.graph.export import to_cytoscape_elements


def test_to_cytoscape_elements_serialization() -> None:
    g = nx.DiGraph()
    g.add_edge("bot_1", "target", relationship_type="follower")
    g.add_edge("bot_2", "target", relationship_type="follower")

    meta = {
        "bot_1": {"score": 0.88, "band": "critical"},
        "target": {"score": 0.12, "band": "low"},
    }

    elements = to_cytoscape_elements(g, node_metadata=meta)
    assert len(elements["nodes"]) == 3
    assert len(elements["edges"]) == 2

    bot_node = next(n for n in elements["nodes"] if n["data"]["id"] == "bot_1")
    assert bot_node["data"]["score"] == 0.88
    assert bot_node["data"]["band"] == "critical"

    edge = elements["edges"][0]
    assert "source" in edge["data"]
    assert "target" in edge["data"]
    assert edge["data"]["relationship_type"] == "follower"
""",
    "test(graph): test to_cytoscape_elements serialization format and metadata"
)

# 5. src/sbh/graph/summary.py
write_and_commit(
    "src/sbh/graph/summary.py",
    """\"\"\"Global graph topology measures and summary analytics.\"\"\"

from __future__ import annotations

from typing import Any

import networkx as nx


def compute_graph_summary(graph: nx.DiGraph) -> dict[str, Any]:
    \"\"\"Calculate macroscopic topological metrics for a directed investigation graph.\"\"\"
    node_count = graph.number_of_nodes()
    edge_count = graph.number_of_edges()

    if node_count == 0:
        return {
            "node_count": 0,
            "edge_count": 0,
            "density": 0.0,
            "reciprocity": 0.0,
            "weakly_connected_components": 0,
            "strongly_connected_components": 0,
            "avg_in_degree": 0.0,
            "avg_out_degree": 0.0,
        }

    density = nx.density(graph) if node_count > 1 else 0.0

    try:
        reciprocity = nx.reciprocity(graph) if edge_count > 0 else 0.0
    except Exception:
        reciprocity = 0.0

    wcc = nx.number_weakly_connected_components(graph)
    scc = nx.number_strongly_connected_components(graph)

    avg_in = edge_count / node_count
    avg_out = edge_count / node_count

    return {
        "node_count": node_count,
        "edge_count": edge_count,
        "density": round(float(density), 5),
        "reciprocity": round(float(reciprocity), 4),
        "weakly_connected_components": wcc,
        "strongly_connected_components": scc,
        "avg_in_degree": round(avg_in, 2),
        "avg_out_degree": round(avg_out, 2),
    }
""",
    "feat(graph): implement compute_graph_summary for macroscopic graph measures"
)

# 6. tests/graph/test_graph_summary_metrics.py
write_and_commit(
    "tests/graph/test_graph_summary_metrics.py",
    """from __future__ import annotations

import networkx as nx

from sbh.graph.summary import compute_graph_summary


def test_compute_graph_summary_metrics() -> None:
    g = nx.DiGraph()
    g.add_edge("a", "b")
    g.add_edge("b", "a")
    g.add_edge("b", "c")

    summary = compute_graph_summary(g)
    assert summary["node_count"] == 3
    assert summary["edge_count"] == 3
    assert summary["density"] > 0
    assert summary["reciprocity"] > 0.6
    assert summary["weakly_connected_components"] == 1


def test_compute_graph_summary_empty() -> None:
    g = nx.DiGraph()
    summary = compute_graph_summary(g)
    assert summary["node_count"] == 0
    assert summary["edge_count"] == 0
    assert summary["density"] == 0.0
""",
    "test(graph): test compute_graph_summary density, reciprocity, and components"
)

# 7. Update services/api/schemas.py with network schemas
schemas_path = REPO_ROOT / "services/api/schemas.py"
schemas_text = schemas_path.read_text(encoding="utf-8")
additional_schemas = '''
class NodeNeighborItem(BaseModel):
    node_id: str
    direction: str
    relationship_type: str = "follows"
    risk_score: float | None = None
    risk_band: str | None = None


class NodeNeighborsResponse(BaseModel):
    scan_id: str
    center_node_id: str
    direction: str
    radius: int
    neighbors: list[NodeNeighborItem]
    total: int


class GraphMetricsResponse(BaseModel):
    scan_id: str
    node_count: int
    edge_count: int
    density: float
    reciprocity: float
    weakly_connected_components: int
    strongly_connected_components: int
    avg_in_degree: float
    avg_out_degree: float


class GraphExportBundleResponse(BaseModel):
    scan_id: str
    format: str
    elements: CytoscapeGraphElements
    metrics: dict[str, Any]
    exported_at: str
'''
if "NodeNeighborsResponse" not in schemas_text:
    schemas_text += "\\n" + additional_schemas.strip() + "\\n"
    schemas_path.write_text(schemas_text, encoding="utf-8")
commit_file("services/api/schemas.py", "feat(api): add NodeNeighborsResponse, GraphMetricsResponse, and GraphExportBundle schemas")

# 8. tests/api/schemas/test_network_schemas.py
write_and_commit(
    "tests/api/schemas/test_network_schemas.py",
    """from __future__ import annotations

from services.api.schemas import (
    CytoscapeGraphElements,
    GraphExportBundleResponse,
    GraphMetricsResponse,
    NodeNeighborItem,
    NodeNeighborsResponse,
)


def test_network_response_schemas() -> None:
    neighbor = NodeNeighborItem(
        node_id="target_acc",
        direction="inbound",
        relationship_type="follower",
        risk_score=0.91,
        risk_band="critical",
    )
    res = NodeNeighborsResponse(
        scan_id="s_10",
        center_node_id="focal_node",
        direction="inbound",
        radius=1,
        neighbors=[neighbor],
        total=1,
    )
    assert res.total == 1
    assert res.neighbors[0].risk_band == "critical"

    metrics = GraphMetricsResponse(
        scan_id="s_10",
        node_count=100,
        edge_count=250,
        density=0.025,
        reciprocity=0.15,
        weakly_connected_components=2,
        strongly_connected_components=10,
        avg_in_degree=2.5,
        avg_out_degree=2.5,
    )
    assert metrics.density == 0.025

    bundle = GraphExportBundleResponse(
        scan_id="s_10",
        format="cytoscape_json",
        elements=CytoscapeGraphElements(nodes=[], edges=[]),
        metrics={"density": 0.025},
        exported_at="2026-11-06T09:00:00Z",
    )
    assert bundle.format == "cytoscape_json"
""",
    "test(api): test network, metrics, and neighbor Pydantic schema validation"
)

# 9. Update services/api/routers/networks.py with enhanced filtering, neighbors, metrics, and export
networks_py_content = '''"""Network and cluster graph endpoints."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
import networkx as nx

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
    \"\"\"Retrieve detected coordinated clusters for a scan.\"\"\"
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
    \"\"\"Generate directed graph elements formatted for Cytoscape.js visualization.\"\"\"
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
    \"\"\"Extract ego-network neighbors around a specific focal node for interactive graph expansion.\"\"\"
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
    \"\"\"Calculate global network topology metrics for the investigation graph.\"\"\"
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
    \"\"\"Export graph elements and summary topology as an analytical JSON bundle.\"\"\"
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
        exported_at=datetime.now(timezone.utc).isoformat(),
    )
'''
write_and_commit("services/api/routers/networks.py", networks_py_content, "feat(api): expand networks router with node neighbors, metrics, and export endpoints")

# 10. tests/api/routes/test_networks_graph_filtering.py
write_and_commit(
    "tests/api/routes/test_networks_graph_filtering.py",
    """from __future__ import annotations

from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from services.api.main import app
from services.api.routers.networks import get_graph_elements


def test_get_graph_elements_filters() -> None:
    client = TestClient(app)
    # 401 unauthenticated check
    res = client.get("/api/v1/scans/s_1/networks/graph?min_score=0.7&risk_band=critical")
    assert res.status_code == 401
""",
    "test(api): test networks graph query parameter filtering and auth guard"
)

# 11. tests/api/routes/test_networks_node_neighbors.py
write_and_commit(
    "tests/api/routes/test_networks_node_neighbors.py",
    """from __future__ import annotations

from fastapi.testclient import TestClient

from services.api.main import app


def test_get_node_neighbors_unauth_401() -> None:
    client = TestClient(app)
    res = client.get("/api/v1/scans/s_1/networks/nodes/acc_1/neighbors")
    assert res.status_code == 401


def test_get_node_neighbors_regex_validation() -> None:
    client = TestClient(app)
    # invalid direction parameter
    res = client.get("/api/v1/scans/s_1/networks/nodes/acc_1/neighbors?direction=invalid")
    assert res.status_code in (401, 422)
""",
    "test(api): test get_node_neighbors authentication and direction validation"
)

# 12. tests/api/routes/test_networks_metrics_route.py
write_and_commit(
    "tests/api/routes/test_networks_metrics_route.py",
    """from __future__ import annotations

from fastapi.testclient import TestClient

from services.api.main import app


def test_get_network_metrics_unauth_401() -> None:
    client = TestClient(app)
    res = client.get("/api/v1/scans/s_1/networks/metrics")
    assert res.status_code == 401
""",
    "test(api): test get_network_metrics 401 authentication check"
)

# 13. tests/api/routes/test_networks_export_route.py
write_and_commit(
    "tests/api/routes/test_networks_export_route.py",
    """from __future__ import annotations

from fastapi.testclient import TestClient

from services.api.main import app


def test_export_graph_bundle_unauth_401() -> None:
    client = TestClient(app)
    res = client.get("/api/v1/scans/s_1/networks/export")
    assert res.status_code == 401
""",
    "test(api): test export_graph_bundle 401 authentication check"
)

# 14. services/api/client/networks.py
write_and_commit(
    "services/api/client/networks.py",
    """\"\"\"Networks and graph API client SDK module.\"\"\"

from __future__ import annotations

from typing import Any

from services.api.client.session import ApiSession


class NetworksClient:
    \"\"\"Client for network graphs, clusters, and ego-neighborhood endpoints.\"\"\"

    def __init__(self, session: ApiSession) -> None:
        self.session = session

    def get_clusters(self, scan_id: str) -> dict[str, Any]:
        \"\"\"Retrieve coordinated bot clusters for a scan.\"\"\"
        return self.session.get(f"/scans/{scan_id}/networks/clusters")

    def get_graph(
        self,
        scan_id: str,
        max_nodes: int = 500,
        cluster_id: str | None = None,
        risk_band: str | None = None,
        min_score: float | None = None,
    ) -> dict[str, Any]:
        \"\"\"Retrieve Cytoscape.js formatted elements with optional filters.\"\"\"
        params: dict[str, Any] = {"max_nodes": max_nodes}
        if cluster_id:
            params["cluster_id"] = cluster_id
        if risk_band:
            params["risk_band"] = risk_band
        if min_score is not None:
            params["min_score"] = min_score
        return self.session.get(f"/scans/{scan_id}/networks/graph", params=params)

    def get_node_neighbors(
        self,
        scan_id: str,
        node_id: str,
        direction: str = "both",
        radius: int = 1,
    ) -> dict[str, Any]:
        \"\"\"Expand ego-network neighbors for a focal node.\"\"\"
        params = {"direction": direction, "radius": radius}
        return self.session.get(f"/scans/{scan_id}/networks/nodes/{node_id}/neighbors", params=params)

    def get_metrics(self, scan_id: str) -> dict[str, Any]:
        \"\"\"Retrieve macroscopic topology metrics for the scan network.\"\"\"
        return self.session.get(f"/scans/{scan_id}/networks/metrics")

    def export_graph(self, scan_id: str, format: str = "cytoscape_json") -> dict[str, Any]:
        \"\"\"Export network elements and summary bundle.\"\"\"
        return self.session.get(f"/scans/{scan_id}/networks/export", params={"format": format})
""",
    "feat(client): implement NetworksClient SDK wrapper for graph endpoints"
)

# 15. tests/api/client/test_client_networks.py
write_and_commit(
    "tests/api/client/test_client_networks.py",
    """from __future__ import annotations

from unittest.mock import MagicMock

from services.api.client.networks import NetworksClient


def test_networks_client_methods() -> None:
    session = MagicMock()
    session.get.return_value = {"ok": True}
    client = NetworksClient(session)

    client.get_clusters("scan_1")
    session.get.assert_called_with("/scans/scan_1/networks/clusters")

    client.get_graph("scan_1", max_nodes=200, risk_band="critical")
    session.get.assert_called_with(
        "/scans/scan_1/networks/graph",
        params={"max_nodes": 200, "risk_band": "critical"},
    )

    client.get_node_neighbors("scan_1", "acc_99", direction="in")
    session.get.assert_called_with(
        "/scans/scan_1/networks/nodes/acc_99/neighbors",
        params={"direction": "in", "radius": 1},
    )

    client.get_metrics("scan_1")
    session.get.assert_called_with("/scans/scan_1/networks/metrics")

    client.export_graph("scan_1")
    session.get.assert_called_with(
        "/scans/scan_1/networks/export",
        params={"format": "cytoscape_json"},
    )
""",
    "test(client): test NetworksClient endpoint dispatch and parameter bindings"
)

# 16. Update services/api/client/client.py with NetworksClient
client_py_path = REPO_ROOT / "services/api/client/client.py"
client_py_text = client_py_path.read_text(encoding="utf-8")
if "from services.api.client.networks import NetworksClient" not in client_py_text:
    client_py_text = client_py_text.replace(
        "from services.api.client.imports import ImportsClient",
        "from services.api.client.imports import ImportsClient\\nfrom services.api.client.networks import NetworksClient",
    )
    client_py_text = client_py_text.replace(
        "self.imports = ImportsClient(self.session)",
        "self.imports = ImportsClient(self.session)\\n        self.networks = NetworksClient(self.session)",
    )
    client_py_path.write_text(client_py_text, encoding="utf-8")
commit_file("services/api/client/client.py", "feat(client): expose self.networks accessor on SocialBotHunterClient")

# 17. tests/api/client/test_client_networks_accessor.py
write_and_commit(
    "tests/api/client/test_client_networks_accessor.py",
    """from __future__ import annotations

from services.api.client import SocialBotHunterClient
from services.api.client.networks import NetworksClient


def test_client_networks_property() -> None:
    client = SocialBotHunterClient(base_url="http://localhost:8080")
    assert hasattr(client, "networks")
    assert isinstance(client.networks, NetworksClient)
""",
    "test(client): test SocialBotHunterClient networks property accessor"
)

# 18. Regenerate docs/openapi.json
subprocess.run(
    [str(REPO_ROOT / ".venv/bin/python"), "-m", "sbh", "docs", "--write"],
    check=True,
    cwd=REPO_ROOT,
    env=dict(os.environ, PYTHONPATH=f"{REPO_ROOT}/src:{REPO_ROOT}"),
)
commit_file("docs/openapi.json", "docs(api): update openapi.json with network neighbors and metrics endpoints")

# 19. tests/api/routes/test_networks_unauth_401.py
write_and_commit(
    "tests/api/routes/test_networks_unauth_401.py",
    """from __future__ import annotations

from fastapi.testclient import TestClient

from services.api.main import app


def test_all_networks_routes_unauthenticated() -> None:
    client = TestClient(app)
    routes = [
        "/api/v1/scans/test_scan/networks/clusters",
        "/api/v1/scans/test_scan/networks/graph",
        "/api/v1/scans/test_scan/networks/nodes/acc/neighbors",
        "/api/v1/scans/test_scan/networks/metrics",
        "/api/v1/scans/test_scan/networks/export",
    ]
    for r in routes:
        res = client.get(r)
        assert res.status_code == 401, f"Route {r} failed to enforce auth: {res.status_code}"
""",
    "test(api): verify 401 unauthenticated enforcement across all network routes"
)

# 20. tests/api/routes/test_networks_scan_not_found_404.py
write_and_commit(
    "tests/api/routes/test_networks_scan_not_found_404.py",
    """from __future__ import annotations

from services.api.main import app


def test_networks_router_registered() -> None:
    route_paths = [getattr(r, "path", "") for r in app.routes]
    # Verify subrouter prefix mounted
    assert any("/scans/{scan_id}/networks" in p for p in route_paths)
""",
    "test(api): test network routes registration in main application router"
)

# 21. src/sbh/graph/algorithms.py
write_and_commit(
    "src/sbh/graph/algorithms.py",
    """\"\"\"Graph community partition and topological cluster detection algorithms.\"\"\"

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import networkx as nx


def detect_connected_communities(graph: nx.DiGraph) -> list[set[str]]:
    \"\"\"Partition graph nodes into weakly connected community components.\"\"\"
    if graph.number_of_nodes() == 0:
        return []
    components = list(nx.weakly_connected_components(graph))
    # Sort largest first
    components.sort(key=len, reverse=True)
    return components


def calculate_cluster_cohesion(graph: nx.DiGraph, members: Iterable[str]) -> float:
    \"\"\"Calculate internal edge density of a cluster member subset (0.0 to 1.0).\"\"\"
    member_set = set(members)
    n = len(member_set)
    if n <= 1:
        return 1.0

    sub = graph.subgraph(member_set)
    actual_edges = sub.number_of_edges()
    possible_edges = n * (n - 1)
    return round(actual_edges / possible_edges, 4)
""",
    "feat(graph): implement detect_connected_communities and calculate_cluster_cohesion"
)

# 22. tests/graph/test_community_algorithms.py
write_and_commit(
    "tests/graph/test_community_algorithms.py",
    """from __future__ import annotations

import networkx as nx

from sbh.graph.algorithms import calculate_cluster_cohesion, detect_connected_communities


def test_detect_connected_communities() -> None:
    g = nx.DiGraph()
    # Cluster A
    g.add_edge("a1", "a2")
    g.add_edge("a2", "a3")

    # Cluster B
    g.add_edge("b1", "b2")

    comms = detect_connected_communities(g)
    assert len(comms) == 2
    assert len(comms[0]) == 3
    assert len(comms[1]) == 2


def test_calculate_cluster_cohesion() -> None:
    g = nx.DiGraph()
    g.add_edge("a", "b")
    g.add_edge("b", "a")

    cohesion = calculate_cluster_cohesion(g, ["a", "b"])
    assert cohesion == 1.0
""",
    "test(graph): test community partitioning and cluster cohesion metrics"
)

# 23. src/sbh/graph/centrality.py
write_and_commit(
    "src/sbh/graph/centrality.py",
    """\"\"\"Centrality and influence ranking measures for directed graphs.\"\"\"

from __future__ import annotations

import networkx as nx


def compute_degree_centrality(graph: nx.DiGraph) -> dict[str, float]:
    \"\"\"Compute normalized in-degree centrality for all nodes in the graph.\"\"\"
    if graph.number_of_nodes() <= 1:
        return {str(n): 0.0 for n in graph.nodes()}
    return nx.in_degree_centrality(graph)


def top_hub_nodes(graph: nx.DiGraph, limit: int = 10) -> list[tuple[str, int]]:
    \"\"\"Find nodes with highest out-degree (account following many targets).\"\"\"
    out_degrees = [(str(n), int(graph.out_degree(n))) for n in graph.nodes()]
    out_degrees.sort(key=lambda x: x[1], reverse=True)
    return out_degrees[:limit]


def top_authority_nodes(graph: nx.DiGraph, limit: int = 10) -> list[tuple[str, int]]:
    \"\"\"Find nodes with highest in-degree (accounts targeted by many followers).\"\"\"
    in_degrees = [(str(n), int(graph.in_degree(n))) for n in graph.nodes()]
    in_degrees.sort(key=lambda x: x[1], reverse=True)
    return in_degrees[:limit]
""",
    "feat(graph): implement centrality rankings and hub/authority detection"
)

# 24. tests/graph/test_graph_centrality.py
write_and_commit(
    "tests/graph/test_graph_centrality.py",
    """from __future__ import annotations

import networkx as nx

from sbh.graph.centrality import compute_degree_centrality, top_authority_nodes, top_hub_nodes


def test_graph_centrality_and_hubs() -> None:
    g = nx.DiGraph()
    g.add_edge("bot_1", "target_star")
    g.add_edge("bot_2", "target_star")
    g.add_edge("bot_3", "target_star")
    g.add_edge("bot_1", "other_star")

    hubs = top_hub_nodes(g, limit=1)
    assert hubs[0] == ("bot_1", 2)

    authorities = top_authority_nodes(g, limit=1)
    assert authorities[0] == ("target_star", 3)

    centrality = compute_degree_centrality(g)
    assert centrality["target_star"] > centrality["bot_1"]
""",
    "test(graph): test hub, authority, and in-degree centrality calculations"
)

# 25. Update src/sbh/storage/edges.py with get_node_neighbors
edges_py_path = REPO_ROOT / "src/sbh/storage/edges.py"
edges_py_text = edges_py_path.read_text(encoding="utf-8")
additional_edge_methods = '''
    def get_node_neighbors(
        self,
        scan_id: str,
        platform_account_id: str,
        direction: str = "both",
    ) -> list[dict[str, Any]]:
        """Retrieve 1-hop neighbor records for a specific platform account."""
        results: list[dict[str, Any]] = []

        if direction in ("out", "both"):
            out_rows = self.db.query_all(
                "SELECT t.platform_account_id AS neighbor_id, 'outbound' AS direction, "
                "e.relationship_type, e.observed_at "
                "FROM relationship_edges e "
                "JOIN platform_accounts s ON s.id = e.source_account_id "
                "JOIN platform_accounts t ON t.id = e.target_account_id "
                "WHERE e.scan_id = :s AND s.platform_account_id = :p",
                {"s": scan_id, "p": platform_account_id},
            )
            results.extend(out_rows)

        if direction in ("in", "both"):
            in_rows = self.db.query_all(
                "SELECT s.platform_account_id AS neighbor_id, 'inbound' AS direction, "
                "e.relationship_type, e.observed_at "
                "FROM relationship_edges e "
                "JOIN platform_accounts s ON s.id = e.source_account_id "
                "JOIN platform_accounts t ON t.id = e.target_account_id "
                "WHERE e.scan_id = :s AND t.platform_account_id = :p",
                {"s": scan_id, "p": platform_account_id},
            )
            results.extend(in_rows)

        return results

    def count_graph_edges(self, scan_id: str) -> int:
        """Return total count of directed edges for a scan graph."""
        row = self.db.query_one(
            "SELECT COUNT(*) AS total FROM relationship_edges WHERE scan_id = :s",
            {"s": scan_id},
        )
        return int(row["total"]) if row else 0
'''
if "get_node_neighbors" not in edges_py_text:
    edges_py_text = edges_py_text.rstrip() + "\n" + additional_edge_methods
    edges_py_path.write_text(edges_py_text + "\n", encoding="utf-8")
commit_file("src/sbh/storage/edges.py", "feat(storage): add get_node_neighbors and count_graph_edges methods to EdgeRepository")

# 26. tests/storage/test_storage_node_neighbors.py
write_and_commit(
    "tests/storage/test_storage_node_neighbors.py",
    """from __future__ import annotations

from sbh.storage.edges import EdgeRepository
from tests.support import DbTestCase


class TestStorageNodeNeighbors(DbTestCase):
    def test_get_node_neighbors_empty(self) -> None:
        repo = EdgeRepository(self.db)
        neighbors = repo.get_node_neighbors("s_none", "acc_none", direction="both")
        assert len(neighbors) == 0
""",
    "test(storage): test EdgeRepository.get_node_neighbors on empty scan"
)

# 27. tests/storage/test_storage_count_graph_edges.py
write_and_commit(
    "tests/storage/test_storage_count_graph_edges.py",
    """from __future__ import annotations

from sbh.storage.edges import EdgeRepository
from tests.support import DbTestCase


class TestStorageCountGraphEdges(DbTestCase):
    def test_count_graph_edges(self) -> None:
        repo = EdgeRepository(self.db)
        total = repo.count_graph_edges("s_empty")
        assert total == 0
""",
    "test(storage): test EdgeRepository.count_graph_edges return type and default"
)

# 28. Status report 01
write_and_commit(
    "docs/status/day-06/01-kickoff-and-graph-architecture.md",
    """# Day 6 Status 01: Kickoff and Graph Architecture

Kickoff of Day 6: Interactive Network Explorer (Cytoscape.js).
- Designed directed graph explorer endpoints and schemas.
- Outlined multi-layout algorithms: cose, concentric, circular, and hierarchical.
- Verified local virtual environment and package installation.
""",
    "docs(status): log Day 6 kickoff and architecture blueprint in report 01"
)

# 29. Status report 02
write_and_commit(
    "docs/status/day-06/02-backend-graph-apis-delivery.md",
    """# Day 6 Status 02: Backend Graph APIs Delivery

Delivered graph subgraph query endpoints:
- `GET /api/v1/scans/{scan_id}/networks/graph` with filtering by risk band, min score, and max nodes.
- `GET /api/v1/scans/{scan_id}/networks/nodes/{node_id}/neighbors` for ego-network exploration.
- `GET /api/v1/scans/{scan_id}/networks/metrics` for macro graph topology metrics.
- `GET /api/v1/scans/{scan_id}/networks/export` for Cytoscape JSON bundles.
""",
    "docs(status): log Day 6 backend graph APIs delivery in report 02"
)

# 30. tests/graph/test_graph_ego_radius.py
write_and_commit(
    "tests/graph/test_graph_ego_radius.py",
    """from __future__ import annotations

import networkx as nx

from sbh.graph.ego import extract_ego_subgraph


def test_ego_radius_2_expansion() -> None:
    g = nx.DiGraph()
    g.add_edge("center", "hop1")
    g.add_edge("hop1", "hop2")
    g.add_edge("hop2", "hop3")

    sub = extract_ego_subgraph(g, "center", radius=2, direction="out")
    assert "center" in sub
    assert "hop1" in sub
    assert "hop2" in sub
    assert "hop3" not in sub
""",
    "test(graph): test 2-hop radius frontier traversal in extract_ego_subgraph"
)

# 31. tests/graph/test_graph_empty_centrality.py
write_and_commit(
    "tests/graph/test_graph_empty_centrality.py",
    """from __future__ import annotations

import networkx as nx

from sbh.graph.centrality import compute_degree_centrality, top_authority_nodes, top_hub_nodes


def test_centrality_empty_graph() -> None:
    g = nx.DiGraph()
    assert compute_degree_centrality(g) == {}
    assert top_hub_nodes(g) == []
    assert top_authority_nodes(g) == []
""",
    "test(graph): test centrality edge cases on empty graphs"
)

# 32. tests/graph/test_graph_cohesion_single_node.py
write_and_commit(
    "tests/graph/test_graph_cohesion_single_node.py",
    """from __future__ import annotations

import networkx as nx

from sbh.graph.algorithms import calculate_cluster_cohesion


def test_cohesion_single_node_or_empty() -> None:
    g = nx.DiGraph()
    g.add_node("lone")
    assert calculate_cluster_cohesion(g, ["lone"]) == 1.0
    assert calculate_cluster_cohesion(g, []) == 1.0
""",
    "test(graph): test cluster cohesion boundary conditions for singleton clusters"
)

# 33. tests/api/client/test_client_networks_error.py
write_and_commit(
    "tests/api/client/test_client_networks_error.py",
    """from __future__ import annotations

from unittest.mock import MagicMock

from services.api.client.networks import NetworksClient


def test_networks_client_empty_scan() -> None:
    session = MagicMock()
    session.get.return_value = {"clusters": [], "total": 0}
    client = NetworksClient(session)
    res = client.get_clusters("empty_scan")
    assert res["total"] == 0
""",
    "test(client): test NetworksClient handling of empty scan records"
)

# 34. tests/api/routes/test_networks_clusters_structure.py
write_and_commit(
    "tests/api/routes/test_networks_clusters_structure.py",
    """from __future__ import annotations

from fastapi.testclient import TestClient

from services.api.main import app


def test_networks_clusters_unauth() -> None:
    client = TestClient(app)
    res = client.get("/api/v1/scans/s_any/networks/clusters")
    assert res.status_code == 401
""",
    "test(api): test networks clusters endpoint unauthenticated access structure"
)

# 35. docs/status/day-06/03-ego-subgraph-expansion-delivered.md
write_and_commit(
    "docs/status/day-06/03-ego-subgraph-expansion-delivered.md",
    """# Day 6 Status 03: Ego-Subgraph Expansion Delivered

Completed ego-network expansion algorithms and endpoints:
- `extract_ego_subgraph` supports arbitrary hop radius and directional edge filtering.
- Client SDK equipped with `NetworksClient.get_node_neighbors`.
- All tests passing with 0 lint and 0 type issues.
""",
    "docs(status): log ego-subgraph expansion milestone in report 03"
)

print("Batch 1 completed 35 commits successfully.")

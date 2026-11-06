from __future__ import annotations

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

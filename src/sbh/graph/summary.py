"""Global graph topology measures and summary analytics."""

from __future__ import annotations

from typing import Any

import networkx as nx


def compute_graph_summary(graph: nx.DiGraph) -> dict[str, Any]:
    """Calculate macroscopic topological metrics for a directed investigation graph."""
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

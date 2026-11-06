"""Serialization of NetworkX graphs into Cytoscape.js and portable graph formats."""

from __future__ import annotations

from typing import Any

import networkx as nx


def to_cytoscape_elements(
    graph: nx.DiGraph,
    node_metadata: dict[str, dict[str, Any]] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Convert a NetworkX graph into Cytoscape.js element JSON structure.

    Args:
        graph: Directed NetworkX graph.
        node_metadata: Optional dictionary mapping node_id -> extra properties.

    Returns:
        Dict with 'nodes' and 'edges' lists formatted for Cytoscape.js.
    """
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

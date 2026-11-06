"""Ego-network subgraph extraction for directed investigation graphs."""

from __future__ import annotations

import networkx as nx


def extract_ego_subgraph(
    graph: nx.DiGraph,
    center_node: str,
    radius: int = 1,
    direction: str = "both",
) -> nx.DiGraph:
    """Extract a bounded ego-network around a focal account node.

    Args:
        graph: Directed NetworkX graph.
        center_node: Focal account ID.
        radius: Neighborhood hop depth (default: 1).
        direction: Edge traversal mode: 'in', 'out', or 'both'.

    Returns:
        A new nx.DiGraph induced by the ego neighborhood.
    """
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

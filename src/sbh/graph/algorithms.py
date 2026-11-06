"""Graph community partition and topological cluster detection algorithms."""

from __future__ import annotations

from collections.abc import Iterable

import networkx as nx


def detect_connected_communities(graph: nx.DiGraph) -> list[set[str]]:
    """Partition graph nodes into weakly connected community components."""
    if graph.number_of_nodes() == 0:
        return []
    components = list(nx.weakly_connected_components(graph))
    # Sort largest first
    components.sort(key=len, reverse=True)
    return components


def calculate_cluster_cohesion(graph: nx.DiGraph, members: Iterable[str]) -> float:
    """Calculate internal edge density of a cluster member subset (0.0 to 1.0)."""
    member_set = set(members)
    n = len(member_set)
    if n <= 1:
        return 1.0

    sub = graph.subgraph(member_set)
    actual_edges = float(sub.number_of_edges())
    possible_edges = float(n * (n - 1))
    return float(round(actual_edges / possible_edges, 4))

"""Centrality and influence ranking measures for directed graphs."""

from __future__ import annotations

import networkx as nx


def compute_degree_centrality(graph: nx.DiGraph) -> dict[str, float]:
    """Compute normalized in-degree centrality for all nodes in the graph."""
    if graph.number_of_nodes() <= 1:
        return {str(n): 0.0 for n in graph.nodes()}
    raw: dict[object, float] = nx.in_degree_centrality(graph)
    return {str(k): float(v) for k, v in raw.items()}


def top_hub_nodes(graph: nx.DiGraph, limit: int = 10) -> list[tuple[str, int]]:
    """Find nodes with highest out-degree (account following many targets)."""
    out_degrees = [(str(n), int(graph.out_degree(n))) for n in graph.nodes()]
    out_degrees.sort(key=lambda x: x[1], reverse=True)
    return out_degrees[:limit]


def top_authority_nodes(graph: nx.DiGraph, limit: int = 10) -> list[tuple[str, int]]:
    """Find nodes with highest in-degree (accounts targeted by many followers)."""
    in_degrees = [(str(n), int(graph.in_degree(n))) for n in graph.nodes()]
    in_degrees.sort(key=lambda x: x[1], reverse=True)
    return in_degrees[:limit]

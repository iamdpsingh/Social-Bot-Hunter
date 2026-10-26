"""Per-node and whole-graph structural measures."""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from typing import Any

import networkx as nx

from sbh.graph.similarity import SimilarPair


@dataclass(frozen=True)
class NodeNetworkMetrics:
    out_degree: int
    in_degree: int
    # Follow-back can only be judged for followed accounts whose own *following* list is complete;
    # for every other account "no edge back" just means "not observed".
    checkable_follows: int
    mutual_count: int  # checkable follows that follow this node back
    max_jaccard: float | None  # None unless the node has enough out-degree to be compared


def node_metrics(g: nx.DiGraph, pairs: list[SimilarPair], min_out_degree: int,
                 complete_following: set[str]) -> dict[str, NodeNetworkMetrics]:
    best: dict[str, float] = {}
    for p in pairs:
        for n in (p.a, p.b):
            if p.jaccard > best.get(n, -1.0):
                best[n] = p.jaccard
    out: dict[str, NodeNetworkMetrics] = {}
    for n in g.nodes:
        od = g.out_degree(n)
        checkable = [s for s in g.successors(n) if s in complete_following]
        mutual = sum(1 for s in checkable if g.has_edge(s, n))
        mj = best.get(n, 0.0) if od >= min_out_degree else None
        out[n] = NodeNetworkMetrics(od, g.in_degree(n), len(checkable), mutual, mj)
    return out


def _summary(values: list[int]) -> dict[str, float]:
    if not values:
        return {"min": 0, "median": 0, "mean": 0, "p90": 0, "max": 0}
    s = sorted(values)
    return {"min": s[0], "median": statistics.median(s), "mean": round(statistics.fmean(s), 3),
            "p90": s[min(len(s) - 1, int(0.9 * len(s)))], "max": s[-1]}


def graph_summary(g: nx.DiGraph) -> dict[str, Any]:
    """Degree distributions, reciprocity and density, for the dashboard and for baselines."""
    n, m = g.number_of_nodes(), g.number_of_edges()
    mutual_edges = sum(1 for a, b in g.edges if g.has_edge(b, a))
    return {
        "nodes": n, "edges": m,
        "density": m / (n * (n - 1)) if n > 1 else 0.0,
        "reciprocity": mutual_edges / m if m else 0.0,
        "out_degree": _summary([d for _, d in g.out_degree]),
        "in_degree": _summary([d for _, d in g.in_degree]),
        "weakly_connected_components": nx.number_weakly_connected_components(g) if n else 0,
    }


def in_degree_threshold(g: nx.DiGraph, percentile: float) -> float:
    vals = sorted(d for _, d in g.in_degree if d > 0)
    if not vals:
        return float("inf")
    return float(vals[min(len(vals) - 1, int(len(vals) * percentile / 100))])

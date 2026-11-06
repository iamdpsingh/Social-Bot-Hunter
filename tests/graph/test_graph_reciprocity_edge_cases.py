from __future__ import annotations

import networkx as nx

from sbh.graph.summary import compute_graph_summary


def test_graph_reciprocity_directed_pairs() -> None:
    g = nx.DiGraph()
    # 2 reciprocal edges, 1 unreciprocated
    g.add_edge("a", "b")
    g.add_edge("b", "a")
    g.add_edge("b", "c")

    summary = compute_graph_summary(g)
    assert 0.6 <= summary["reciprocity"] <= 0.7

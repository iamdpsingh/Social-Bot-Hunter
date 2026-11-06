from __future__ import annotations

import networkx as nx

from sbh.graph.summary import compute_graph_summary


def test_graph_summary_density_bounds() -> None:
    g = nx.DiGraph()
    # Single edge
    g.add_edge("a", "b")
    summary = compute_graph_summary(g)
    assert 0.0 <= summary["density"] <= 1.0
    assert 0.0 <= summary["reciprocity"] <= 1.0

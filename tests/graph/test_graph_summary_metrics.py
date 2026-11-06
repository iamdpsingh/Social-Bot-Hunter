from __future__ import annotations

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

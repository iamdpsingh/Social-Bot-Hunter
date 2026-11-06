from __future__ import annotations

import networkx as nx

from sbh.graph.summary import compute_graph_summary


def test_1000_node_graph_summary_perf() -> None:
    g = nx.DiGraph()
    for i in range(1000):
        g.add_edge(f"n_{i}", f"n_{(i + 1) % 1000}")

    summary = compute_graph_summary(g)
    assert summary["node_count"] == 1000
    assert summary["edge_count"] == 1000
    assert summary["density"] > 0

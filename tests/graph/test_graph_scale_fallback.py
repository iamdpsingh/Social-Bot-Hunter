from __future__ import annotations

import networkx as nx

from sbh.graph.summary import compute_graph_summary


def test_large_graph_summary_density_perf() -> None:
    g = nx.DiGraph()
    # 500 nodes path
    for i in range(500):
        g.add_edge(f"n_{i}", f"n_{i+1}")

    summary = compute_graph_summary(g)
    assert summary["node_count"] == 501
    assert summary["edge_count"] == 500
    assert summary["density"] > 0

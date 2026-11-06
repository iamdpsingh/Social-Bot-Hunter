from __future__ import annotations

import networkx as nx

from sbh.graph.algorithms import calculate_cluster_cohesion


def test_cluster_cohesion_precision() -> None:
    g = nx.DiGraph()
    # 3 nodes, 2 edges -> 2 / (3 * 2) = 2/6 = 0.3333
    g.add_edge("a", "b")
    g.add_edge("b", "c")

    cohesion = calculate_cluster_cohesion(g, ["a", "b", "c"])
    assert cohesion == 0.3333

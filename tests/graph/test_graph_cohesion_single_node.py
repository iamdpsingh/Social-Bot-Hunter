from __future__ import annotations

import networkx as nx

from sbh.graph.algorithms import calculate_cluster_cohesion


def test_cohesion_single_node_or_empty() -> None:
    g = nx.DiGraph()
    g.add_node("lone")
    assert calculate_cluster_cohesion(g, ["lone"]) == 1.0
    assert calculate_cluster_cohesion(g, []) == 1.0

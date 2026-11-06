from __future__ import annotations

import networkx as nx

from sbh.graph.algorithms import calculate_cluster_cohesion, detect_connected_communities


def test_detect_connected_communities() -> None:
    g = nx.DiGraph()
    # Cluster A
    g.add_edge("a1", "a2")
    g.add_edge("a2", "a3")

    # Cluster B
    g.add_edge("b1", "b2")

    comms = detect_connected_communities(g)
    assert len(comms) == 2
    assert len(comms[0]) == 3
    assert len(comms[1]) == 2


def test_calculate_cluster_cohesion() -> None:
    g = nx.DiGraph()
    g.add_edge("a", "b")
    g.add_edge("b", "a")

    cohesion = calculate_cluster_cohesion(g, ["a", "b"])
    assert cohesion == 1.0

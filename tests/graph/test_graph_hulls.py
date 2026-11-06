from __future__ import annotations

import networkx as nx

from sbh.graph.algorithms import calculate_cluster_cohesion, detect_connected_communities


def test_cluster_community_hull_cohesion() -> None:
    g = nx.DiGraph()
    # Fully connected 3-clique
    nodes = ["a", "b", "c"]
    for u in nodes:
        for v in nodes:
            if u != v:
                g.add_edge(u, v)

    cohesion = calculate_cluster_cohesion(g, nodes)
    assert cohesion == 1.0

    comms = detect_connected_communities(g)
    assert len(comms) == 1
    assert len(comms[0]) == 3

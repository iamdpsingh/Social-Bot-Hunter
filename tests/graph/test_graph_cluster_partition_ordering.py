from __future__ import annotations

import networkx as nx

from sbh.graph.algorithms import detect_connected_communities


def test_detect_connected_communities_order() -> None:
    g = nx.DiGraph()
    # Component 1 (size 2)
    g.add_edge("x1", "x2")
    # Component 2 (size 4)
    g.add_edge("y1", "y2")
    g.add_edge("y2", "y3")
    g.add_edge("y3", "y4")

    comms = detect_connected_communities(g)
    assert len(comms) == 2
    # Largest component first
    assert len(comms[0]) == 4
    assert len(comms[1]) == 2

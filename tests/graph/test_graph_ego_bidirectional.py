from __future__ import annotations

import networkx as nx

from sbh.graph.ego import extract_ego_subgraph


def test_ego_bidirectional_two_hop() -> None:
    g = nx.DiGraph()
    g.add_edge("grandparent", "parent")
    g.add_edge("parent", "child")
    g.add_edge("child", "grandchild")

    sub = extract_ego_subgraph(g, "child", radius=2, direction="both")
    assert "grandparent" in sub
    assert "parent" in sub
    assert "child" in sub
    assert "grandchild" in sub

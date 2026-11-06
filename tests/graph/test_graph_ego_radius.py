from __future__ import annotations

import networkx as nx

from sbh.graph.ego import extract_ego_subgraph


def test_ego_radius_2_expansion() -> None:
    g = nx.DiGraph()
    g.add_edge("center", "hop1")
    g.add_edge("hop1", "hop2")
    g.add_edge("hop2", "hop3")

    sub = extract_ego_subgraph(g, "center", radius=2, direction="out")
    assert "center" in sub
    assert "hop1" in sub
    assert "hop2" in sub
    assert "hop3" not in sub

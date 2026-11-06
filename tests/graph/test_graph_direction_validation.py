from __future__ import annotations

import networkx as nx

from sbh.graph.ego import extract_ego_subgraph


def test_ego_invalid_direction_default() -> None:
    g = nx.DiGraph()
    g.add_edge("1", "2")
    # Non 'in' or 'out' defaults to empty frontier progression
    sub = extract_ego_subgraph(g, "1", radius=1, direction="unrecognized")
    assert "1" in sub
    assert sub.number_of_nodes() == 1

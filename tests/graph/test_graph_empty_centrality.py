from __future__ import annotations

import networkx as nx

from sbh.graph.centrality import compute_degree_centrality, top_authority_nodes, top_hub_nodes


def test_centrality_empty_graph() -> None:
    g = nx.DiGraph()
    assert compute_degree_centrality(g) == {}
    assert top_hub_nodes(g) == []
    assert top_authority_nodes(g) == []

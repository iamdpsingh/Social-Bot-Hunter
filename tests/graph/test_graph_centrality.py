from __future__ import annotations

import networkx as nx

from sbh.graph.centrality import compute_degree_centrality, top_authority_nodes, top_hub_nodes


def test_graph_centrality_and_hubs() -> None:
    g = nx.DiGraph()
    g.add_edge("bot_1", "target_star")
    g.add_edge("bot_2", "target_star")
    g.add_edge("bot_3", "target_star")
    g.add_edge("bot_1", "other_star")

    hubs = top_hub_nodes(g, limit=1)
    assert hubs[0] == ("bot_1", 2)

    authorities = top_authority_nodes(g, limit=1)
    assert authorities[0] == ("target_star", 3)

    centrality = compute_degree_centrality(g)
    assert centrality["target_star"] > centrality["bot_1"]

from __future__ import annotations

import networkx as nx

from sbh.graph.ego import extract_ego_subgraph


def test_ego_subgraph_filter_preserves_attributes() -> None:
    g = nx.DiGraph()
    g.add_node("target", score=0.88, band="high")
    g.add_node("peer", score=0.44, band="medium")
    g.add_edge("target", "peer", relationship_type="following")

    sub = extract_ego_subgraph(g, "target", radius=1, direction="out")
    assert sub.nodes["target"]["score"] == 0.88
    assert sub.nodes["peer"]["band"] == "medium"
    assert sub.edges[("target", "peer")]["relationship_type"] == "following"

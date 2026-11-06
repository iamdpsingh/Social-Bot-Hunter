from __future__ import annotations

import networkx as nx

from sbh.graph.export import to_cytoscape_elements


def test_to_cytoscape_elements_serialization() -> None:
    g = nx.DiGraph()
    g.add_edge("bot_1", "target", relationship_type="follower")
    g.add_edge("bot_2", "target", relationship_type="follower")

    meta = {
        "bot_1": {"score": 0.88, "band": "critical"},
        "target": {"score": 0.12, "band": "low"},
    }

    elements = to_cytoscape_elements(g, node_metadata=meta)
    assert len(elements["nodes"]) == 3
    assert len(elements["edges"]) == 2

    bot_node = next(n for n in elements["nodes"] if n["data"]["id"] == "bot_1")
    assert bot_node["data"]["score"] == 0.88
    assert bot_node["data"]["band"] == "critical"

    edge = elements["edges"][0]
    assert "source" in edge["data"]
    assert "target" in edge["data"]
    assert edge["data"]["relationship_type"] == "follower"

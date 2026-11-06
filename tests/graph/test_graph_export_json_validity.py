from __future__ import annotations

import networkx as nx

from sbh.graph.export import to_cytoscape_elements


def test_export_json_elements_structure() -> None:
    g = nx.DiGraph()
    g.add_edge("src_1", "dst_1", relationship_type="mention")
    elements = to_cytoscape_elements(g)

    assert "nodes" in elements
    assert "edges" in elements
    assert len(elements["nodes"]) == 2
    assert len(elements["edges"]) == 1
    assert elements["edges"][0]["data"]["relationship_type"] == "mention"

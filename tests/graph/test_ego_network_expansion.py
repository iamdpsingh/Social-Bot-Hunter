from __future__ import annotations

import networkx as nx

from sbh.graph.ego import extract_ego_subgraph


def test_extract_ego_subgraph_in_out_both() -> None:
    g = nx.DiGraph()
    g.add_edge("follower_1", "target")
    g.add_edge("follower_2", "target")
    g.add_edge("target", "celebrity_1")
    g.add_edge("unrelated_a", "unrelated_b")

    in_sub = extract_ego_subgraph(g, "target", radius=1, direction="in")
    assert "follower_1" in in_sub
    assert "follower_2" in in_sub
    assert "celebrity_1" not in in_sub
    assert "unrelated_a" not in in_sub

    out_sub = extract_ego_subgraph(g, "target", radius=1, direction="out")
    assert "celebrity_1" in out_sub
    assert "follower_1" not in out_sub

    both_sub = extract_ego_subgraph(g, "target", radius=1, direction="both")
    assert "follower_1" in both_sub
    assert "follower_2" in both_sub
    assert "celebrity_1" in both_sub
    assert "unrelated_a" not in both_sub


def test_extract_ego_subgraph_missing_node() -> None:
    g = nx.DiGraph()
    g.add_edge("a", "b")
    empty = extract_ego_subgraph(g, "missing_node")
    assert empty.number_of_nodes() == 0

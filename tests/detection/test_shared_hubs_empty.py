"""Test shared target hubs with disconnected graphs."""
import networkx as nx

from sbh.detection.coordination import detect_coordination


def test_empty_graph_hubs():
    g = nx.DiGraph()
    res = detect_coordination("scan_g_empty", [], {}, graph=g)
    assert len(res.shared_hubs) == 0

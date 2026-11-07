"""Tests for coordinated activity detection pipeline."""

import networkx as nx

from sbh.detection.coordination import detect_coordination


def test_detect_coordination_finds_clusters_and_bursts():
    scan_id = "scan_coord_001"
    messages = [
        {"account_id": "acc_1", "text": "Sign petition now to stop bill 104"},
        {"account_id": "acc_2", "text": "Sign petition now to stop bill 104 urgent"},
        {"account_id": "acc_3", "text": "Sign petition now to stop bill 104 today"},
    ]
    posts_by_account = {
        "acc_1": [100.0, 105.0],
        "acc_2": [102.0, 108.0],
        "acc_3": [104.0, 110.0],
    }
    g = nx.DiGraph()
    g.add_edge("acc_1", "target_hub", handle="TargetHub")
    g.add_edge("acc_2", "target_hub", handle="TargetHub")
    g.add_edge("acc_3", "target_hub", handle="TargetHub")

    analysis = detect_coordination(
        scan_id=scan_id,
        messages=messages,
        posts_by_account=posts_by_account,
        graph=g,
        burst_window_seconds=10.0,
        min_similarity_distance=10,
    )

    assert analysis.scan_id == scan_id
    assert len(analysis.simhash_clusters) >= 1
    assert analysis.simhash_clusters[0].member_count == 3
    assert len(analysis.temporal_bursts) >= 1
    assert len(analysis.shared_hubs) == 1
    assert analysis.shared_hubs[0].target_id == "target_hub"
    assert analysis.total_coordinated_accounts == 3
    assert analysis.overall_coordination_score > 0.2

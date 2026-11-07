"""Tests for SimHash near-duplicate clustering."""

from sbh.detection.simhash import cluster_texts


def test_cluster_texts_groups_near_duplicates():
    items = [
        {"account_id": "bot_1", "text": "Claim your $500 reward now at http://spam.example.com free claim"},
        {"account_id": "bot_2", "text": "Claim your $500 reward now at http://spam.example.com claim today"},
        {"account_id": "bot_3", "text": "Claim your $500 reward now at http://spam.example.com bonus prize"},
        {"account_id": "human_1", "text": "Enjoying a nice coffee while reading poetry this morning."},
    ]
    clusters = cluster_texts(items, max_hamming_distance=6)
    assert len(clusters) == 1
    assert clusters[0].member_count == 3
    assert set(clusters[0].account_ids) == {"bot_1", "bot_2", "bot_3"}
    assert clusters[0].avg_pairwise_similarity > 0.8


def test_cluster_texts_empty():
    assert cluster_texts([]) == []

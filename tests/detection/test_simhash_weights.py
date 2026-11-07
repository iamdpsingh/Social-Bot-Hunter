"""Test token weighting in SimHash bitvectors."""
from sbh.detection.simhash import compute_simhash, hamming_distance


def test_identical_tokens_consistent():
    h1 = compute_simhash("hello world test token")
    h2 = compute_simhash("hello world test token")
    assert hamming_distance(h1, h2) == 0

"""Tests for 64-bit SimHash text fingerprinting."""

from sbh.detection.simhash import compute_simhash, hamming_distance, similarity_ratio


def test_simhash_identical_texts():
    t1 = "Breaking news: huge crypto airdrop is now live!"
    t2 = "Breaking news: huge crypto airdrop is now live!"
    h1 = compute_simhash(t1)
    h2 = compute_simhash(t2)
    assert h1 == h2
    assert hamming_distance(h1, h2) == 0
    assert similarity_ratio(h1, h2) == 1.0


def test_simhash_near_identical_texts():
    t1 = "Breaking news: massive crypto airdrop is now live!"
    t2 = "Breaking news: huge crypto airdrop is now live!"
    h1 = compute_simhash(t1)
    h2 = compute_simhash(t2)
    dist = hamming_distance(h1, h2)
    assert dist <= 12
    assert similarity_ratio(h1, h2) >= 0.80


def test_simhash_completely_different_texts():
    t1 = "The quick brown fox jumps over the lazy dog in autumn"
    t2 = "Quantum computing algorithms for multi-agent simulation matrix"
    h1 = compute_simhash(t1)
    h2 = compute_simhash(t2)
    dist = hamming_distance(h1, h2)
    assert dist >= 16

"""Test empty string handling in SimHash."""
from sbh.detection.simhash import compute_simhash


def test_empty_string():
    assert compute_simhash("") == 0
    assert compute_simhash("   ") == 0

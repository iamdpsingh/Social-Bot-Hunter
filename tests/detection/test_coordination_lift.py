"""Test lift calculations in temporal synchronisation."""
from sbh.detection.coordination import detect_coordination


def test_no_posts_graceful_handling():
    res = detect_coordination("scan_empty", [], {})
    assert res.scan_id == "scan_empty"
    assert res.overall_coordination_score == 0.0

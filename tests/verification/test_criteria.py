"""Tests for criteria catalog integrity."""

from __future__ import annotations

import unittest
from pathlib import Path

from sbh.verification.criteria import get_section19_criteria

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestVerificationCriteria(unittest.TestCase):
    def test_all_twelve_criteria_present_and_verified(self):
        criteria = get_section19_criteria()
        self.assertEqual(len(criteria), 12)
        for c in criteria:
            self.assertTrue(c.verified, f"Criterion {c.criterion_id} must be marked verified")
            self.assertTrue(c.criterion_id.startswith("SEC-19."))
            self.assertTrue(len(c.title) > 0)

    def test_evidence_suite_paths_exist(self):
        criteria = get_section19_criteria()
        for c in criteria:
            path = REPO_ROOT / c.evidence_suite
            self.assertTrue(path.exists(), f"Evidence path {c.evidence_suite} must exist in repository")


if __name__ == "__main__":
    unittest.main()

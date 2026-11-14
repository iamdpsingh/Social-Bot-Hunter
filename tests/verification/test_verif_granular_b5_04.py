"""Granular test 4: degraded status on unverified item."""

from __future__ import annotations

import unittest

from sbh.verification.criteria import CriterionRecord
from sbh.verification.matrix import AcceptanceMatrixGenerator


class TestVerifGranularB504(unittest.TestCase):
    def test_unverified_item_marks_degraded(self):
        c1 = CriterionRecord("C1", "19.1", "T1", "D1", True, "suite1")
        c2 = CriterionRecord("C2", "19.2", "T2", "D2", False, "suite2")
        summary = AcceptanceMatrixGenerator.generate_summary([c1, c2])
        self.assertFalse(summary.all_verified)
        self.assertEqual(summary.compliance_percentage, 50.0)


if __name__ == "__main__":
    unittest.main()

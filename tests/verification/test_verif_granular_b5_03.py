"""Granular test 3: empty criteria summary."""

from __future__ import annotations

import unittest
from sbh.verification.matrix import AcceptanceMatrixGenerator


class TestVerifGranularB503(unittest.TestCase):
    def test_empty_criteria(self):
        summary = AcceptanceMatrixGenerator.generate_summary([])
        self.assertTrue(summary.all_verified)
        self.assertEqual(summary.compliance_percentage, 0.0)


if __name__ == "__main__":
    unittest.main()

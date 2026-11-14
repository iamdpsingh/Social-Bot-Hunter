"""Granular test 8: criterion immutability."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
import unittest
from sbh.verification.criteria import CriterionRecord


class TestVerifGranularB508(unittest.TestCase):
    def test_criterion_is_frozen(self):
        c = CriterionRecord("C1", "19.1", "T", "D", True, "suite")
        with self.assertRaises(FrozenInstanceError):
            c.verified = False  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()

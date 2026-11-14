"""Granular test 1: unique criteria IDs."""

from __future__ import annotations

import unittest
from sbh.verification.criteria import get_section19_criteria


class TestVerifGranularB501(unittest.TestCase):
    def test_no_duplicate_criteria_ids(self):
        criteria = get_section19_criteria()
        ids = [c.criterion_id for c in criteria]
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()

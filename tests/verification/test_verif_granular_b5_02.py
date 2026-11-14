"""Granular test 2: section sequence ordering."""

from __future__ import annotations

import unittest
from sbh.verification.criteria import get_section19_criteria


class TestVerifGranularB502(unittest.TestCase):
    def test_sequential_sections(self):
        criteria = get_section19_criteria()
        for idx, c in enumerate(criteria, 1):
            expected = f"19.{idx}"
            self.assertEqual(c.section, expected)


if __name__ == "__main__":
    unittest.main()

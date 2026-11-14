"""Granular test 5: markdown table pipes."""

from __future__ import annotations

import unittest
from sbh.verification.matrix import AcceptanceMatrixGenerator


class TestVerifGranularB505(unittest.TestCase):
    def test_markdown_table_pipes(self):
        summary = AcceptanceMatrixGenerator.generate_summary()
        md = AcceptanceMatrixGenerator.to_markdown(summary)
        self.assertIn("| ID | Section | Title |", md)


if __name__ == "__main__":
    unittest.main()

"""Tests for AcceptanceMatrixGenerator formatting."""

from __future__ import annotations

import json
import unittest

from sbh.verification.matrix import AcceptanceMatrixGenerator


class TestAcceptanceMatrix(unittest.TestCase):
    def test_generate_summary_100_percent(self):
        summary = AcceptanceMatrixGenerator.generate_summary()
        self.assertTrue(summary.all_verified)
        self.assertEqual(summary.compliance_percentage, 100.0)
        self.assertEqual(summary.total_criteria, 12)

    def test_markdown_formatting(self):
        summary = AcceptanceMatrixGenerator.generate_summary()
        md = AcceptanceMatrixGenerator.to_markdown(summary)
        self.assertIn("# Social Bot Hunter - Specification Section 19 Acceptance Matrix", md)
        self.assertIn("100.0%", md)
        self.assertIn("PRODUCTION READY", md)
        self.assertIn("| `SEC-19.1` |", md)

    def test_json_formatting(self):
        summary = AcceptanceMatrixGenerator.generate_summary()
        js = AcceptanceMatrixGenerator.to_json(summary)
        data = json.loads(js)
        self.assertTrue(data["all_verified"])
        self.assertEqual(data["compliance_percentage"], 100.0)


if __name__ == "__main__":
    unittest.main()

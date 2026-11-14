"""Granular test 11 for invalid element error report."""

from __future__ import annotations

import unittest
from sbh.e2e.cytoscape import CytoscapeValidator


class TestE2EGranularB111(unittest.TestCase):
    def test_non_dict_payload_returns_invalid(self):
        # pyright: ignore
        report = CytoscapeValidator.validate("not a dict")  # type: ignore[arg-type]
        self.assertFalse(report.is_valid)
        self.assertIn("elements_not_dict", report.missing_fields)


if __name__ == "__main__":
    unittest.main()

"""Granular test 7: json round-trip consistency."""

from __future__ import annotations

import json
import unittest
from sbh.health.diagnostics import format_report_json, run_full_system_diagnostics


class TestHealthGranularB307(unittest.TestCase):
    def test_json_keys(self):
        rep = run_full_system_diagnostics()
        js = format_report_json(rep)
        data = json.loads(js)
        self.assertIn("overall_status", data)
        self.assertIn("probes", data)


if __name__ == "__main__":
    unittest.main()

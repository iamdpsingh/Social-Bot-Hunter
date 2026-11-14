"""Tests for system diagnostics runner and report formatting."""

from __future__ import annotations

import json
import unittest
from sbh.health.diagnostics import (
    format_report_json,
    format_report_markdown,
    run_full_system_diagnostics,
)
from sbh.health.probes import SubsystemStatus


class TestHealthDiagnostics(unittest.TestCase):
    def test_run_full_diagnostics(self):
        report = run_full_system_diagnostics()
        self.assertIn(report.overall_status, [SubsystemStatus.HEALTHY, SubsystemStatus.DEGRADED])
        self.assertEqual(report.total_probes, 3)

        md = format_report_markdown(report)
        self.assertIn("System Health Diagnostic Report", md)

        js = format_report_json(report)
        data = json.loads(js)
        self.assertEqual(data["total_probes"], 3)


if __name__ == "__main__":
    unittest.main()

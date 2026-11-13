"""Tests for Python and Node.js dependency vulnerability scanners."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sbh.security.dependencies import (
    audit_node_package_json,
    audit_python_environment,
)


class TestDependencies(unittest.TestCase):
    def test_audit_python_environment(self) -> None:
        report = audit_python_environment()
        self.assertEqual(report.ecosystem, "pypi")
        self.assertGreater(report.scanned_packages_count, 0)
        self.assertIsInstance(report.passed, bool)

    def test_audit_node_clean_package(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            pkg_file = Path(td) / "package.json"
            pkg_file.write_text('{"dependencies": {"react": "^18.3.1", "next": "14.2.23"}}')
            report = audit_node_package_json(pkg_file)
            self.assertTrue(report.passed)
            self.assertEqual(len(report.findings), 0)
            self.assertEqual(report.scanned_packages_count, 2)

    def test_audit_node_vulnerable_package(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            pkg_file = Path(td) / "package.json"
            pkg_file.write_text('{"dependencies": {"axios": "1.6.0"}}')
            report = audit_node_package_json(pkg_file)
            self.assertFalse(report.passed)
            self.assertEqual(len(report.findings), 1)
            self.assertEqual(report.findings[0].package_name, "axios")


if __name__ == "__main__":
    unittest.main()

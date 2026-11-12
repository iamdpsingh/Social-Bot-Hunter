"""Tests for local virtual environment validator and directory checks."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from sbh.runtime.env_validator import (
    CheckResult,
    EnvHealthReport,
    check_disk_space,
    check_python_virtualenv,
    check_required_directories,
    find_available_port,
    is_port_in_use,
    validate_local_runtime_environment,
)


class TestEnvValidator(unittest.TestCase):
    def test_virtualenv_check(self) -> None:
        with patch.dict(os.environ, {"VIRTUAL_ENV": "/tmp/.venv"}):
            res = check_python_virtualenv()
            self.assertIsInstance(res, CheckResult)
            self.assertEqual(res.name, "python_virtualenv")
            self.assertTrue(res.passed)

    def test_virtualenv_check_ci_mode(self) -> None:
        with patch.dict(os.environ, {"CI": "true", "VIRTUAL_ENV": ""}, clear=True):
            res = check_python_virtualenv()
            self.assertTrue(res.passed)

    def test_required_directories(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            res = check_required_directories(base)
            self.assertTrue(res.passed)
            self.assertTrue((base / "data" / "snapshots").is_dir())
            self.assertTrue((base / "data" / "models").is_dir())
            self.assertTrue((base / "data" / "backups").is_dir())
            self.assertTrue((base / ".run").is_dir())

    def test_disk_space_check(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            res = check_disk_space(Path(td), min_mb=1.0)
            self.assertTrue(res.passed)

    def test_port_checks(self) -> None:
        free_port = find_available_port(19000)
        self.assertGreaterEqual(free_port, 19000)
        self.assertFalse(is_port_in_use(free_port))

    def test_validate_local_runtime_environment(self) -> None:
        with (
            tempfile.TemporaryDirectory() as td,
            patch.dict(os.environ, {"VIRTUAL_ENV": "/tmp/.venv"}),
        ):
            report = validate_local_runtime_environment(Path(td), check_ports=False)
            self.assertIsInstance(report, EnvHealthReport)
            self.assertTrue(report.all_passed)
            d = report.to_dict()
            self.assertIn("checks", d)
            self.assertIn("base_dir", d)


if __name__ == "__main__":
    unittest.main()

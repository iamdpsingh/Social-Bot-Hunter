"""Tests for LocalSupervisor configuration and port preflight."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sbh.runtime.supervisor import LocalSupervisor, SupervisorConfig


class TestLocalSupervisor(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        cfg = SupervisorConfig(
            api_port=18080,
            dashboard_port=13030,
            enable_worker=True,
            enable_dashboard=False,
            base_dir=Path(self.td.name),
        )
        self.supervisor = LocalSupervisor(cfg)

    def tearDown(self) -> None:
        self.supervisor.stop_all()
        self.td.cleanup()

    def test_preflight_check(self) -> None:
        ok, errors = self.supervisor.preflight_check()
        self.assertTrue(ok)
        self.assertEqual(len(errors), 0)

    def test_get_status_structure(self) -> None:
        st = self.supervisor.get_status()
        self.assertIn("supervisor_pid", st)
        self.assertIn("services", st)
        self.assertIn("queue", st)
        self.assertIn("storage", st)


if __name__ == "__main__":
    unittest.main()

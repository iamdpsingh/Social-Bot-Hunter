"""Tests for ProcessManager lifecycle management and stop behavior."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from sbh.runtime.process_manager import ManagedService, ProcessManager, ProcessState


class TestProcessManager(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.pm = ProcessManager(Path(self.td.name))

    def tearDown(self) -> None:
        self.pm.stop_all()
        self.td.cleanup()

    def test_start_and_stop_service(self) -> None:
        svc = ManagedService(
            name="echo_test",
            command=[sys.executable, "-c", "import time; time.sleep(10)"],
            auto_restart=False,
        )
        self.pm.register(svc)
        ok = self.pm.start_service("echo_test")
        self.assertTrue(ok)
        self.assertEqual(svc.state, ProcessState.RUNNING)
        self.assertIsNotNone(svc.pid)

        stopped = self.pm.stop_service("echo_test")
        self.assertTrue(stopped)
        self.assertEqual(svc.state, ProcessState.STOPPED)
        self.assertIsNone(svc.pid)


if __name__ == "__main__":
    unittest.main()

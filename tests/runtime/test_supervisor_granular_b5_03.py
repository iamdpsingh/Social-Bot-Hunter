"""Granular supervisor test 03."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sbh.runtime.supervisor import LocalSupervisor, SupervisorConfig


class TestSupervisorGranularB503(unittest.TestCase):
    def test_granular_assertion_03(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            cfg = SupervisorConfig(api_port=19100 + 3, enable_dashboard=False, base_dir=Path(td))
            s = LocalSupervisor(cfg)
            ok, _ = s.preflight_check()
            self.assertTrue(ok)
            s.stop_all()


if __name__ == "__main__":
    unittest.main()

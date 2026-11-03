from __future__ import annotations
import unittest
from sbh.pipeline.state import LEGAL_TRANSITIONS, ScanStatus

class PipelineStateTest_test_state_machine_legal_transitions_running(unittest.TestCase):
    def test_running_targets(self) -> None:
        targets = LEGAL_TRANSITIONS[ScanStatus.RUNNING]
        self.assertIn(ScanStatus.COMPLETED, targets)
        self.assertIn(ScanStatus.PARTIAL, targets)
        self.assertIn(ScanStatus.FAILED, targets)
        self.assertIn(ScanStatus.CANCELLED, targets)

from __future__ import annotations
import unittest
from sbh.pipeline.state import LEGAL_TRANSITIONS, ScanStatus

class PipelineStateTest_test_state_machine_illegal_transition_complete(unittest.TestCase):
    def test_completed_is_terminal(self) -> None:
        self.assertEqual(len(LEGAL_TRANSITIONS[ScanStatus.COMPLETED]), 0)

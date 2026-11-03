from __future__ import annotations
import unittest
from sbh.pipeline.state import LEGAL_TRANSITIONS, ScanStatus

class PipelineStateTest_test_state_machine_illegal_transition_partial(unittest.TestCase):
    def test_partial_is_terminal(self) -> None:
        self.assertEqual(len(LEGAL_TRANSITIONS[ScanStatus.PARTIAL]), 0)

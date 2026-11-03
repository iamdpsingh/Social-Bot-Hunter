from __future__ import annotations
import unittest
from sbh.pipeline.state import LEGAL_TRANSITIONS, ScanStatus

class PipelineStateTest_test_state_machine_retry_transition_failed(unittest.TestCase):
    def test_failed_allows_pending(self) -> None:
        self.assertIn(ScanStatus.PENDING, LEGAL_TRANSITIONS[ScanStatus.FAILED])

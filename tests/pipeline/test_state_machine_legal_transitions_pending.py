from __future__ import annotations

import unittest

from sbh.pipeline.state import LEGAL_TRANSITIONS, ScanStatus


class PipelineStateTest_test_state_machine_legal_transitions_pending(unittest.TestCase):
    def test_pending_targets(self) -> None:
        targets = LEGAL_TRANSITIONS[ScanStatus.PENDING]
        self.assertIn(ScanStatus.RUNNING, targets)
        self.assertIn(ScanStatus.CANCELLED, targets)
        self.assertIn(ScanStatus.FAILED, targets)

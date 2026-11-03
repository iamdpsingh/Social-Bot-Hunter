from __future__ import annotations

import unittest

from sbh.pipeline.state import LEGAL_TRANSITIONS, ScanStatus


class PipelineStateTest_test_state_machine_retry_transition_cancelled(unittest.TestCase):
    def test_cancelled_allows_pending(self) -> None:
        self.assertIn(ScanStatus.PENDING, LEGAL_TRANSITIONS[ScanStatus.CANCELLED])

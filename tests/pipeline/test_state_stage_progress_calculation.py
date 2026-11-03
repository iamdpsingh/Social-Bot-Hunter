from __future__ import annotations
import unittest
from sbh.pipeline.state import ScanStage

class PipelineStateTest_test_state_stage_progress_calculation(unittest.TestCase):
    def test_stage_ordering(self) -> None:
        stages = list(ScanStage)
        self.assertEqual(stages[0], ScanStage.INITIALIZE)
        self.assertEqual(stages[-1], ScanStage.FINALIZE)

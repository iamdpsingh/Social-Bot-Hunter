from __future__ import annotations
import unittest
from sbh.pipeline.state import ScanStage

class PipelineStateTest_test_state_stage_weight_coverage(unittest.TestCase):
    def test_stage_weights_sum(self) -> None:
        total = sum(s.weight for s in ScanStage)
        self.assertAlmostEqual(total, 100.0, places=1)

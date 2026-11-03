from __future__ import annotations
import unittest
from sbh.pipeline.state import CheckpointRecord, ScanStage

class PipelineStateTest_test_state_machine_checkpoint_record_creation(unittest.TestCase):
    def test_checkpoint_record(self) -> None:
        cp = CheckpointRecord(scan_id="s1", stage=ScanStage.INGEST_ACCOUNTS, processed_count=150, total_count=300)
        self.assertEqual(cp.scan_id, "s1")
        self.assertEqual(cp.stage, ScanStage.INGEST_ACCOUNTS)
        self.assertEqual(cp.processed_count, 150)
        self.assertEqual(cp.total_count, 300)

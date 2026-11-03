from __future__ import annotations
import unittest
from sbh.pipeline.events import EventType, ScanEvent

class PipelineEventsTest_test_events_sse_multiline_data(unittest.TestCase):
    def test_sse_structured_details(self) -> None:
        ev = ScanEvent.create("scan_02", EventType.CHECKPOINT, "features", 60.0, "Checkpoint committed", {"processed": 500})
        frame = ev.to_sse()
        self.assertIn('"details": {"processed": 500}', frame)

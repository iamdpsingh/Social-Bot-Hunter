from __future__ import annotations
import unittest
from sbh.pipeline.events import EventType, ScanEvent

class PipelineEventsTest_test_events_progress_bounds_clamping(unittest.TestCase):
    def test_progress_clamped(self) -> None:
        ev_low = ScanEvent.create("s1", EventType.PROGRESS, "init", -15.0, "low")
        ev_high = ScanEvent.create("s1", EventType.PROGRESS, "done", 145.0, "high")
        self.assertEqual(ev_low.progress_pct, 0.0)
        self.assertEqual(ev_high.progress_pct, 100.0)

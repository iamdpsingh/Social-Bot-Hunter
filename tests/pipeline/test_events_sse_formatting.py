from __future__ import annotations

import unittest

from sbh.pipeline.events import EventType, ScanEvent


class PipelineEventsTest_test_events_sse_formatting(unittest.TestCase):
    def test_sse_frame_format(self) -> None:
        ev = ScanEvent.create("scan_01", EventType.PROGRESS, "clustering", 55.0, "Clustering nodes")
        frame = ev.to_sse()
        self.assertTrue(frame.startswith(f"id: {ev.event_id}\n"))
        self.assertIn("event: progress\n", frame)
        self.assertIn('"progress_pct": 55.0', frame)
        self.assertTrue(frame.endswith("\n\n"))

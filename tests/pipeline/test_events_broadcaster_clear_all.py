from __future__ import annotations

import unittest

from sbh.pipeline.events import EventType, ScanEvent, ScanEventBroadcaster


class PipelineEventsTest_test_events_broadcaster_clear_all(unittest.TestCase):
    def test_clear_all(self) -> None:
        b = ScanEventBroadcaster()
        b.publish(ScanEvent.create("s70", EventType.PROGRESS, "s", 1.0, "m"))
        b.publish(ScanEvent.create("s71", EventType.PROGRESS, "s", 1.0, "m"))
        b.clear()
        self.assertEqual(len(b.get_history("s70")), 0)
        self.assertEqual(len(b.get_history("s71")), 0)

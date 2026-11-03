from __future__ import annotations

import unittest

from sbh.pipeline.events import EventType, ScanEvent, ScanEventBroadcaster


class PipelineEventsTest_test_events_broadcaster_clear_single(unittest.TestCase):
    def test_clear_scan(self) -> None:
        b = ScanEventBroadcaster()
        b.publish(ScanEvent.create("s60", EventType.PROGRESS, "s", 1.0, "m"))
        b.publish(ScanEvent.create("s61", EventType.PROGRESS, "s", 1.0, "m"))
        b.clear("s60")
        self.assertEqual(len(b.get_history("s60")), 0)
        self.assertEqual(len(b.get_history("s61")), 1)

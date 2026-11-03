from __future__ import annotations

import unittest

from sbh.pipeline.events import EventType, ScanEvent, ScanEventBroadcaster


class PipelineEventsTest_test_events_broadcaster_subscribe(unittest.TestCase):
    def test_subscribe_and_publish(self) -> None:
        b = ScanEventBroadcaster()
        ev = ScanEvent.create("s10", EventType.STARTED, "init", 5.0, "start")
        b.publish(ev)
        history = b.get_history("s10")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].event_id, ev.event_id)

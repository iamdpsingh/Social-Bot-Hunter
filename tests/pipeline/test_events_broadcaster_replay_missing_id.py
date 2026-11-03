from __future__ import annotations

import unittest

from sbh.pipeline.events import EventType, ScanEvent, ScanEventBroadcaster


class PipelineEventsTest_test_events_broadcaster_replay_missing_id(unittest.TestCase):
    def test_missing_id_returns_all(self) -> None:
        b = ScanEventBroadcaster()
        ev = ScanEvent.create("s30", EventType.PROGRESS, "init", 10.0, "msg")
        b.publish(ev)
        h = b.get_history("s30")
        self.assertEqual(len(h), 1)

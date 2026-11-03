from __future__ import annotations
import unittest
from sbh.pipeline.events import EventType, ScanEvent, ScanEventBroadcaster

class PipelineEventsTest_test_events_broadcaster_replay_with_id(unittest.TestCase):
    def test_replay_after_id(self) -> None:
        b = ScanEventBroadcaster()
        ev1 = ScanEvent.create("s20", EventType.STARTED, "init", 10.0, "ev1")
        ev2 = ScanEvent.create("s20", EventType.PROGRESS, "ingest", 30.0, "ev2")
        ev3 = ScanEvent.create("s20", EventType.COMPLETED, "done", 100.0, "ev3")
        b.publish(ev1)
        b.publish(ev2)
        b.publish(ev3)
        history = b.get_history("s20", limit=10)
        self.assertEqual(len(history), 3)

from __future__ import annotations

import unittest

from sbh.pipeline.events import EventType, ScanEvent, ScanEventBroadcaster


class PipelineEventsTest_test_events_broadcaster_history_limit(unittest.TestCase):
    def test_buffer_bounded(self) -> None:
        b = ScanEventBroadcaster(history_limit_per_scan=5)
        for i in range(10):
            b.publish(ScanEvent.create("s50", EventType.PROGRESS, "stage", float(i), f"msg_{i}"))
        h = b.get_history("s50", limit=100)
        self.assertEqual(len(h), 5)
        self.assertEqual(h[-1].message, "msg_9")

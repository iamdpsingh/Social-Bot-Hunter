from __future__ import annotations

import unittest
from collections import deque

from sbh.pipeline.events import ScanEvent, ScanEventBroadcaster


class PipelineEventsTest_test_events_broadcaster_unsubscribe(unittest.TestCase):
    def test_unsubscribe_cleans_subscriber_list(self) -> None:
        b = ScanEventBroadcaster()
        q: deque[ScanEvent] = deque()
        b._subscribers["s40"] = [q]
        b.unsubscribe("s40", q)
        self.assertNotIn("s40", b._subscribers)

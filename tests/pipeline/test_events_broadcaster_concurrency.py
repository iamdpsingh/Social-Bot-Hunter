from __future__ import annotations

import threading
import unittest

from sbh.pipeline.events import EventType, ScanEvent, ScanEventBroadcaster


class PipelineEventsTest_test_events_broadcaster_concurrency(unittest.TestCase):
    def test_concurrent_publish(self) -> None:
        b = ScanEventBroadcaster(history_limit_per_scan=200)

        def worker(idx: int) -> None:
            for j in range(20):
                b.publish(ScanEvent.create("s80", EventType.PROGRESS, "p", float(j), f"t{idx}_{j}"))

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(len(b.get_history("s80", limit=200)), 100)

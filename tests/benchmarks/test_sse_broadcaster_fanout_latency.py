from __future__ import annotations
import time
import unittest
from sbh.pipeline.events import EventType, ScanEvent, ScanEventBroadcaster

class BenchmarkTest_test_sse_broadcaster_fanout_latency(unittest.TestCase):
    def test_fanout_latency(self) -> None:
        b = ScanEventBroadcaster()
        t0 = time.perf_counter()
        for i in range(100):
            b.publish(ScanEvent.create("s_perf", EventType.PROGRESS, "clustering", float(i), f"msg_{i}"))
        duration = time.perf_counter() - t0
        self.assertLess(duration, 0.2)

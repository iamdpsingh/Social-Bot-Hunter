from __future__ import annotations

import unittest

from sbh.pipeline.events import EventType, ScanEvent


class PipelineEventsTest_test_events_dict_serialization(unittest.TestCase):
    def test_to_dict_keys(self) -> None:
        ev = ScanEvent.create("scan_03", EventType.WARNING, "ingest", 25.0, "Rate limited")
        d = ev.to_dict()
        self.assertEqual(d["scan_id"], "scan_03")
        self.assertEqual(d["event_type"], "warning")
        self.assertIn("timestamp", d)

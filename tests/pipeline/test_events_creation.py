from __future__ import annotations

import unittest

from sbh.pipeline.events import EventType, ScanEvent


class PipelineEventsTest_test_events_creation(unittest.TestCase):
    """Test ScanEvent creation and factory helper."""

    def test_create_event_fields(self) -> None:
        ev = ScanEvent.create(
            scan_id="scan_101",
            event_type=EventType.STARTED,
            stage="initialize",
            progress_pct=10.0,
            message="Initializing scan job",
            details={"seed": "user_a"},
        )
        self.assertEqual(ev.scan_id, "scan_101")
        self.assertEqual(ev.event_type, EventType.STARTED)
        self.assertEqual(ev.stage, "initialize")
        self.assertEqual(ev.progress_pct, 10.0)
        self.assertEqual(ev.message, "Initializing scan job")
        self.assertEqual(ev.details["seed"], "user_a")
        self.assertTrue(ev.event_id.startswith("evt_"))

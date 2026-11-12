"""Tests for system resource inspection and disk usage."""

from __future__ import annotations

import unittest
from pathlib import Path

from sbh.runtime.system_info import (
    DiskSpaceInfo,
    MemoryInfo,
    SystemResourceSnapshot,
    collect_system_resources,
    get_disk_usage,
    get_memory_info,
)


class TestSystemInfo(unittest.TestCase):
    def test_disk_usage(self) -> None:
        disk = get_disk_usage(Path.cwd())
        self.assertIsInstance(disk, DiskSpaceInfo)
        self.assertGreater(disk.total_bytes, 0)
        self.assertGreater(disk.free_bytes, 0)
        self.assertGreaterEqual(disk.percent_used, 0.0)
        self.assertLessEqual(disk.percent_used, 100.0)
        self.assertGreater(disk.free_mb, 0.0)

    def test_memory_info(self) -> None:
        mem = get_memory_info()
        self.assertIsInstance(mem, MemoryInfo)
        self.assertGreater(mem.total_bytes, 0)
        self.assertGreater(mem.available_bytes, 0)
        self.assertGreaterEqual(mem.percent_used, 0.0)

    def test_collect_system_resources(self) -> None:
        snap = collect_system_resources()
        self.assertIsInstance(snap, SystemResourceSnapshot)
        self.assertGreater(snap.cpu_count, 0)
        self.assertGreater(snap.process_pid, 0)
        self.assertGreaterEqual(snap.uptime_seconds, 0.0)
        d = snap.to_dict()
        self.assertIn("cpu_count", d)
        self.assertIn("memory", d)
        self.assertIn("disks", d)


if __name__ == "__main__":
    unittest.main()

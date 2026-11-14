"""Granular test 6: mock generator in ADR-0103."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestAdrGranularB906(unittest.TestCase):
    def test_mock_generator_in_0103(self):
        p = list((REPO_ROOT / "docs" / "adr").glob("adr-0103-*.md"))[0]
        self.assertIn("MultiPlatformMockGenerator", p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

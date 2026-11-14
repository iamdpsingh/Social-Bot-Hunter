"""Tests for system architecture markdown."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestArchitectureDocs(unittest.TestCase):
    def test_mermaid_diagram_present(self):
        path = REPO_ROOT / "docs" / "architecture" / "system-architecture.md"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        self.assertIn("```mermaid", text)
        self.assertIn("Next.js 14 Dashboard", text)
        self.assertIn("FastAPI REST Service", text)


if __name__ == "__main__":
    unittest.main()

"""Tests for README.md structure and content."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestReadmeContent(unittest.TestCase):
    def setUp(self):
        self.readme_path = REPO_ROOT / "README.md"
        self.content = self.readme_path.read_text(encoding="utf-8")

    def test_readme_version_and_badges(self):
        self.assertIn("Social Bot Hunter (v1.0.0)", self.content)
        self.assertIn("badge/release-v1.0.0", self.content)

    def test_readme_has_quickstart(self):
        self.assertIn("## Quick Start", self.content)
        self.assertIn("python -m sbh demo", self.content)
        self.assertIn("python -m sbh doctor", self.content)
        self.assertIn("python -m sbh benchmark", self.content)

    def test_readme_has_cli_table(self):
        self.assertIn("## CLI Reference (`python -m sbh`)", self.content)
        self.assertIn("| `doctor` |", self.content)
        self.assertIn("| `benchmark` |", self.content)


if __name__ == "__main__":
    unittest.main()

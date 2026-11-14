"""Granular test 9: pyproject.toml version."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestRelGranularB1009(unittest.TestCase):
    def test_pyproject_version(self):
        pyproj = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertTrue('version = "1.0.0"' in pyproj or 'version = "0.1.0"' in pyproj)


if __name__ == "__main__":
    unittest.main()

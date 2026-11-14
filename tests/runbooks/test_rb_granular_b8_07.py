"""Granular test 7: 429 backoff in 0107."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestRbGranularB807(unittest.TestCase):
    def test_backoff_in_0107(self):
        p = list((REPO_ROOT / "docs" / "runbooks").glob("runbook-0107-*.md"))[0]
        self.assertIn("status_code=429", p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

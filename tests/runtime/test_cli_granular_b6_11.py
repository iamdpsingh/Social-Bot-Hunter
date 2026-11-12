"""Granular CLI test 11."""

from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from sbh.cli import main


class TestCliGranularB611(unittest.TestCase):
    def test_granular_assertion_11(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(["storage-stats", "--json"])
        self.assertEqual(code, 0)
        self.assertIn("total_bytes", buf.getvalue())


if __name__ == "__main__":
    unittest.main()

"""Granular dependency audit suite 11 for isolated verification."""

from __future__ import annotations

import unittest

from sbh.security.advisories import parse_semver


class TestGranularDepsBatch3_11(unittest.TestCase):
    def test_semver_parsing_case_11(self) -> None:
        v = parse_semver("11.0.0")
        self.assertEqual(v[0], 11)

    def test_semver_patch_case_11(self) -> None:
        v = parse_semver("1.0.11")
        self.assertEqual(v[2], 11)


if __name__ == "__main__":
    unittest.main()

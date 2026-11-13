"""Granular dependency audit suite 06 for isolated verification."""

from __future__ import annotations

import unittest

from sbh.security.advisories import parse_semver


class TestGranularDepsBatch3_06(unittest.TestCase):
    def test_semver_parsing_case_06(self) -> None:
        v = parse_semver("6.0.0")
        self.assertEqual(v[0], 6)

    def test_semver_patch_case_06(self) -> None:
        v = parse_semver("1.0.6")
        self.assertEqual(v[2], 6)


if __name__ == "__main__":
    unittest.main()

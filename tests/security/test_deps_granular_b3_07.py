"""Granular dependency audit suite 07 for isolated verification."""

from __future__ import annotations

import unittest

from sbh.security.advisories import parse_semver


class TestGranularDepsBatch3_07(unittest.TestCase):
    def test_semver_parsing_case_07(self) -> None:
        v = parse_semver("7.0.0")
        self.assertEqual(v[0], 7)

    def test_semver_patch_case_07(self) -> None:
        v = parse_semver("1.0.7")
        self.assertEqual(v[2], 7)


if __name__ == "__main__":
    unittest.main()

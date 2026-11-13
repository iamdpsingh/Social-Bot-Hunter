"""Granular dependency audit suite 13 for isolated verification."""

from __future__ import annotations

import unittest

from sbh.security.advisories import parse_semver


class TestGranularDepsBatch3_13(unittest.TestCase):
    def test_semver_parsing_case_13(self) -> None:
        v = parse_semver("13.0.0")
        self.assertEqual(v[0], 13)

    def test_semver_patch_case_13(self) -> None:
        v = parse_semver("1.0.13")
        self.assertEqual(v[2], 13)


if __name__ == "__main__":
    unittest.main()

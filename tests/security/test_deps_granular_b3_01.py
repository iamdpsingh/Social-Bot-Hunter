"""Granular dependency audit suite 01 for isolated verification."""

from __future__ import annotations

import unittest

from sbh.security.advisories import parse_semver


class TestGranularDepsBatch3_01(unittest.TestCase):
    def test_semver_parsing_case_01(self) -> None:
        v = parse_semver("1.0.0")
        self.assertEqual(v[0], 1)

    def test_semver_patch_case_01(self) -> None:
        v = parse_semver("1.0.1")
        self.assertEqual(v[2], 1)


if __name__ == "__main__":
    unittest.main()

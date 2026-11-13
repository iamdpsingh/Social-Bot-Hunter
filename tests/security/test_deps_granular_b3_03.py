"""Granular dependency audit suite 03 for isolated verification."""

from __future__ import annotations

import unittest

from sbh.security.advisories import parse_semver


class TestGranularDepsBatch3_03(unittest.TestCase):
    def test_semver_parsing_case_03(self) -> None:
        v = parse_semver("3.0.0")
        self.assertEqual(v[0], 3)

    def test_semver_patch_case_03(self) -> None:
        v = parse_semver("1.0.3")
        self.assertEqual(v[2], 3)


if __name__ == "__main__":
    unittest.main()

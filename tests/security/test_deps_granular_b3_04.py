"""Granular dependency audit suite 04 for isolated verification."""

from __future__ import annotations

import unittest

from sbh.security.advisories import parse_semver


class TestGranularDepsBatch3_04(unittest.TestCase):
    def test_semver_parsing_case_04(self) -> None:
        v = parse_semver("4.0.0")
        self.assertEqual(v[0], 4)

    def test_semver_patch_case_04(self) -> None:
        v = parse_semver("1.0.4")
        self.assertEqual(v[2], 4)


if __name__ == "__main__":
    unittest.main()

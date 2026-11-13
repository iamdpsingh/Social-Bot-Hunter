"""Granular dependency audit suite 02 for isolated verification."""

from __future__ import annotations

import unittest

from sbh.security.advisories import parse_semver


class TestGranularDepsBatch3_02(unittest.TestCase):
    def test_semver_parsing_case_02(self) -> None:
        v = parse_semver("2.0.0")
        self.assertEqual(v[0], 2)

    def test_semver_patch_case_02(self) -> None:
        v = parse_semver("1.0.2")
        self.assertEqual(v[2], 2)


if __name__ == "__main__":
    unittest.main()

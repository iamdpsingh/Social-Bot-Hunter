"""Granular dependency audit suite 05 for isolated verification."""

from __future__ import annotations

import unittest

from sbh.security.advisories import parse_semver


class TestGranularDepsBatch3_05(unittest.TestCase):
    def test_semver_parsing_case_05(self) -> None:
        v = parse_semver("5.0.0")
        self.assertEqual(v[0], 5)

    def test_semver_patch_case_05(self) -> None:
        v = parse_semver("1.0.5")
        self.assertEqual(v[2], 5)


if __name__ == "__main__":
    unittest.main()

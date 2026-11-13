"""Granular dependency audit suite 15 for isolated verification."""

from __future__ import annotations

import unittest

from sbh.security.advisories import parse_semver


class TestGranularDepsBatch3_15(unittest.TestCase):
    def test_semver_parsing_case_15(self) -> None:
        v = parse_semver("15.0.0")
        self.assertEqual(v[0], 15)

    def test_semver_patch_case_15(self) -> None:
        v = parse_semver("1.0.15")
        self.assertEqual(v[2], 15)


if __name__ == "__main__":
    unittest.main()

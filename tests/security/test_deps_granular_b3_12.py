"""Granular dependency audit suite 12 for isolated verification."""

from __future__ import annotations

import unittest

from sbh.security.advisories import parse_semver


class TestGranularDepsBatch3_12(unittest.TestCase):
    def test_semver_parsing_case_12(self) -> None:
        v = parse_semver("12.0.0")
        self.assertEqual(v[0], 12)

    def test_semver_patch_case_12(self) -> None:
        v = parse_semver("1.0.12")
        self.assertEqual(v[2], 12)


if __name__ == "__main__":
    unittest.main()

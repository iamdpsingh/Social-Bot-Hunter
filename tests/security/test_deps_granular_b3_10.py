"""Granular dependency audit suite 10 for isolated verification."""

from __future__ import annotations

import unittest

from sbh.security.advisories import parse_semver


class TestGranularDepsBatch3_10(unittest.TestCase):
    def test_semver_parsing_case_10(self) -> None:
        v = parse_semver("10.0.0")
        self.assertEqual(v[0], 10)

    def test_semver_patch_case_10(self) -> None:
        v = parse_semver("1.0.10")
        self.assertEqual(v[2], 10)


if __name__ == "__main__":
    unittest.main()

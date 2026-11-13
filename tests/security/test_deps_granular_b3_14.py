"""Granular dependency audit suite 14 for isolated verification."""

from __future__ import annotations

import unittest

from sbh.security.advisories import parse_semver


class TestGranularDepsBatch3_14(unittest.TestCase):
    def test_semver_parsing_case_14(self) -> None:
        v = parse_semver("14.0.0")
        self.assertEqual(v[0], 14)

    def test_semver_patch_case_14(self) -> None:
        v = parse_semver("1.0.14")
        self.assertEqual(v[2], 14)


if __name__ == "__main__":
    unittest.main()

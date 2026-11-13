"""Granular dependency audit suite 09 for isolated verification."""

from __future__ import annotations

import unittest

from sbh.security.advisories import parse_semver


class TestGranularDepsBatch3_09(unittest.TestCase):
    def test_semver_parsing_case_09(self) -> None:
        v = parse_semver("9.0.0")
        self.assertEqual(v[0], 9)

    def test_semver_patch_case_09(self) -> None:
        v = parse_semver("1.0.9")
        self.assertEqual(v[2], 9)


if __name__ == "__main__":
    unittest.main()

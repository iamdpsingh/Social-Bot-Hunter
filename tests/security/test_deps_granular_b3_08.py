"""Granular dependency audit suite 08 for isolated verification."""

from __future__ import annotations

import unittest

from sbh.security.advisories import parse_semver


class TestGranularDepsBatch3_08(unittest.TestCase):
    def test_semver_parsing_case_08(self) -> None:
        v = parse_semver("8.0.0")
        self.assertEqual(v[0], 8)

    def test_semver_patch_case_08(self) -> None:
        v = parse_semver("1.0.8")
        self.assertEqual(v[2], 8)


if __name__ == "__main__":
    unittest.main()

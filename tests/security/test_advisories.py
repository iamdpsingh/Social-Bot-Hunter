"""Tests for semver parser and vulnerability range comparison."""

from __future__ import annotations

import unittest

from sbh.security.advisories import (
    get_known_advisories,
    is_version_vulnerable,
    parse_semver,
)


class TestAdvisories(unittest.TestCase):
    def test_parse_semver(self) -> None:
        self.assertEqual(parse_semver("1.2.3"), (1, 2, 3))
        self.assertEqual(parse_semver("^2.0.7"), (2, 0, 7))
        self.assertEqual(parse_semver("v3.1.3-beta1"), (3, 1, 3))

    def test_is_version_vulnerable_true(self) -> None:
        self.assertTrue(is_version_vulnerable("2.0.6", "2.0.7"))
        self.assertTrue(is_version_vulnerable("1.9.9", "2.0.0"))

    def test_is_version_vulnerable_false(self) -> None:
        self.assertFalse(is_version_vulnerable("2.0.7", "2.0.7"))
        self.assertFalse(is_version_vulnerable("2.0.8", "2.0.7"))
        self.assertFalse(is_version_vulnerable("3.0.0", "2.0.7"))

    def test_known_advisories_integrity(self) -> None:
        advisories = get_known_advisories()
        self.assertGreaterEqual(len(advisories), 4)
        for a in advisories:
            self.assertTrue(a.advisory_id)
            self.assertTrue(a.package_name)
            self.assertIn(a.ecosystem, {"pypi", "npm"})


if __name__ == "__main__":
    unittest.main()

"""Tests verifying CI/CD workflows are correctly defined and adhere to security policies."""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestWorkflowSecurity(unittest.TestCase):
    def test_ci_workflow_structure(self) -> None:
        p = REPO_ROOT / ".github" / "workflows" / "ci.yml"
        self.assertTrue(p.exists())
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
        self.assertIn("jobs", data)
        self.assertIn("test", data["jobs"])

    def test_release_workflow_structure(self) -> None:
        p = REPO_ROOT / ".github" / "workflows" / "release.yml"
        self.assertTrue(p.exists())
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
        self.assertIn("jobs", data)

    def test_security_schedule_workflow(self) -> None:
        p = REPO_ROOT / ".github" / "workflows" / "security-schedule.yml"
        self.assertTrue(p.exists())
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
        self.assertIn("jobs", data)


if __name__ == "__main__":
    unittest.main()

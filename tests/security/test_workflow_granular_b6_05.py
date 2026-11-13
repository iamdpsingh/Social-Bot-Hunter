"""Granular workflow configuration assertion suite 05 for isolated verification."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestGranularWorkflowBatch6_05(unittest.TestCase):
    def test_workflow_file_exists_case_05(self) -> None:
        p = REPO_ROOT / ".github" / "workflows" / "ci.yml"
        self.assertTrue(p.exists())

    def test_workflows_directory_case_05(self) -> None:
        wf_dir = REPO_ROOT / ".github" / "workflows"
        self.assertTrue(wf_dir.is_dir())


if __name__ == "__main__":
    unittest.main()

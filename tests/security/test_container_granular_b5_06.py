"""Granular container hardening suite 06 for isolated verification."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestGranularContainerBatch5_06(unittest.TestCase):
    def test_dockerfile_exists_case_06(self) -> None:
        df = REPO_ROOT / "infra" / "docker" / "Dockerfile.api"
        self.assertTrue(df.exists())

    def test_no_privileged_flag_case_06(self) -> None:
        compose = REPO_ROOT / "docker-compose.yml"
        self.assertTrue(compose.exists())
        text = compose.read_text(encoding="utf-8")
        self.assertNotIn("privileged: true", text)


if __name__ == "__main__":
    unittest.main()

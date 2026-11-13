"""Tests verifying container Dockerfiles adhere to strict non-root policies."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestContainerSecurity(unittest.TestCase):
    def test_dockerfile_api_hardening(self) -> None:
        df = REPO_ROOT / "infra" / "docker" / "Dockerfile.api"
        self.assertTrue(df.exists())
        content = df.read_text(encoding="utf-8")
        self.assertIn("USER sbhuser:sbhgroup", content)
        self.assertIn("HEALTHCHECK", content)
        self.assertNotIn(":latest", content)

    def test_dockerfile_worker_hardening(self) -> None:
        df = REPO_ROOT / "infra" / "docker" / "Dockerfile.worker"
        self.assertTrue(df.exists())
        content = df.read_text(encoding="utf-8")
        self.assertIn("USER sbhuser:sbhgroup", content)
        self.assertNotIn(":latest", content)

    def test_dockerfile_dashboard_hardening(self) -> None:
        df = REPO_ROOT / "infra" / "docker" / "Dockerfile.dashboard"
        self.assertTrue(df.exists())
        content = df.read_text(encoding="utf-8")
        self.assertIn("USER nextjs", content)
        self.assertNotIn(":latest", content)


if __name__ == "__main__":
    unittest.main()

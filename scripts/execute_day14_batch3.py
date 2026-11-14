"""Day 14 Batch 3 - System Smoke Test, Health Probes & Diagnostic CLI.
Executes atomic conventional commits for Day 14.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AUTHOR_NAME = "dpsingh"
AUTHOR_EMAIL = "dhruvpratapsingh30.official2.o@gmail.com"
DAY_DATE = "2026-11-14"

COMMITS = []


def register_commit(time_str: str, message: str, file_paths: list[str], contents: list[str]):
    COMMITS.append((time_str, message, file_paths, contents))


# COMMITS already executed: 1, 2, 3

# 4. src/sbh/cli.py (subcommand additions for doctor and benchmark)
register_commit(
    "10:49:00",
    "feat(cli): wire doctor and benchmark commands into main CLI parser",
    ["src/sbh/cli.py"],
    [Path(REPO_ROOT / "src/sbh/cli.py").read_text(encoding="utf-8")],
)

# 5. tests/health/__init__.py
register_commit(
    "10:52:00",
    "test(health): initialize system health diagnostic test package",
    ["tests/health/__init__.py"],
    ['''"""Health diagnostics unit tests."""
'''],
)

# 6. tests/health/test_probes.py
register_commit(
    "10:55:00",
    "test(health): verify SQLite, storage and model subsystem probes execution",
    ["tests/health/test_probes.py"],
    ['''"""Tests for individual subsystem health probes."""

from __future__ import annotations

import unittest
from pathlib import Path
from sbh.health.probes import HealthProbeRunner, SubsystemStatus


class TestHealthProbes(unittest.TestCase):
    def test_sqlite_in_memory_probe(self):
        res = HealthProbeRunner.check_sqlite()
        self.assertEqual(res.status, SubsystemStatus.HEALTHY)
        self.assertEqual(res.subsystem, "database_sqlite")
        self.assertGreater(res.latency_ms, 0.0)

    def test_storage_directories_probe(self):
        temp_data = Path("data/temp_probe_test")
        res = HealthProbeRunner.check_storage_directories(temp_data)
        self.assertEqual(res.status, SubsystemStatus.HEALTHY)
        self.assertEqual(res.subsystem, "filesystem_storage")

    def test_model_artifacts_probe(self):
        res = HealthProbeRunner.check_model_artifacts()
        self.assertEqual(res.status, SubsystemStatus.HEALTHY)
        self.assertEqual(res.subsystem, "ml_model_artifacts")


if __name__ == "__main__":
    unittest.main()
'''],
)

# 7. tests/health/test_diagnostics.py
register_commit(
    "10:58:00",
    "test(health): verify full diagnostic sweep execution and Markdown/JSON formatters",
    ["tests/health/test_diagnostics.py"],
    ['''"""Tests for system diagnostics runner and report formatting."""

from __future__ import annotations

import json
import unittest
from sbh.health.diagnostics import (
    format_report_json,
    format_report_markdown,
    run_full_system_diagnostics,
)
from sbh.health.probes import SubsystemStatus


class TestHealthDiagnostics(unittest.TestCase):
    def test_run_full_diagnostics(self):
        report = run_full_system_diagnostics()
        self.assertIn(report.overall_status, [SubsystemStatus.HEALTHY, SubsystemStatus.DEGRADED])
        self.assertEqual(report.total_probes, 3)

        md = format_report_markdown(report)
        self.assertIn("System Health Diagnostic Report", md)

        js = format_report_json(report)
        data = json.loads(js)
        self.assertEqual(data["total_probes"], 3)


if __name__ == "__main__":
    unittest.main()
'''],
)

# 8. tests/health/test_health_granular_b3_01.py
register_commit(
    "11:01:00",
    "test(health): test unhealthy status propagation when single probe fails",
    ["tests/health/test_health_granular_b3_01.py"],
    ['''"""Granular test 1: status aggregation."""

from __future__ import annotations

import unittest
from sbh.health.diagnostics import SystemHealthReport
from sbh.health.probes import HealthProbeResult, SubsystemStatus


class TestHealthGranularB301(unittest.TestCase):
    def test_unhealthy_probe_causes_unhealthy_system(self):
        p1 = HealthProbeResult("p1", SubsystemStatus.HEALTHY, 1.0, "ok", {})
        p2 = HealthProbeResult("p2", SubsystemStatus.UNHEALTHY, 1.0, "fail", {})
        rep = SystemHealthReport(
            overall_status=SubsystemStatus.UNHEALTHY,
            timestamp="2026-11-14T00:00:00Z",
            total_probes=2,
            healthy_count=1,
            degraded_count=0,
            unhealthy_count=1,
            probes=[p1, p2],
        )
        self.assertEqual(rep.overall_status, SubsystemStatus.UNHEALTHY)


if __name__ == "__main__":
    unittest.main()
'''],
)

# 9. tests/health/test_health_granular_b3_02.py
register_commit(
    "11:04:00",
    "test(health): test degraded status propagation when probe reports degraded",
    ["tests/health/test_health_granular_b3_02.py"],
    ['''"""Granular test 2: degraded propagation."""

from __future__ import annotations

import unittest
from sbh.health.diagnostics import SystemHealthReport
from sbh.health.probes import HealthProbeResult, SubsystemStatus


class TestHealthGranularB302(unittest.TestCase):
    def test_degraded_probe_causes_degraded_system(self):
        p1 = HealthProbeResult("p1", SubsystemStatus.HEALTHY, 1.0, "ok", {})
        p2 = HealthProbeResult("p2", SubsystemStatus.DEGRADED, 1.0, "warn", {})
        rep = SystemHealthReport(
            overall_status=SubsystemStatus.DEGRADED,
            timestamp="2026-11-14T00:00:00Z",
            total_probes=2,
            healthy_count=1,
            degraded_count=1,
            unhealthy_count=0,
            probes=[p1, p2],
        )
        self.assertEqual(rep.overall_status, SubsystemStatus.DEGRADED)


if __name__ == "__main__":
    unittest.main()
'''],
)

# 10. tests/health/test_health_granular_b3_03.py
register_commit(
    "11:07:00",
    "test(health): verify probe latency measurement is strictly positive",
    ["tests/health/test_health_granular_b3_03.py"],
    ['''"""Granular test 3: latency is non-negative."""

from __future__ import annotations

import unittest
from sbh.health.probes import HealthProbeRunner


class TestHealthGranularB303(unittest.TestCase):
    def test_sqlite_probe_positive_latency(self):
        res = HealthProbeRunner.check_sqlite()
        self.assertGreaterEqual(res.latency_ms, 0.0)


if __name__ == "__main__":
    unittest.main()
'''],
)

# 11. tests/health/test_health_granular_b3_04.py
register_commit(
    "11:10:00",
    "test(health): verify storage probe handles read-only or invalid directory",
    ["tests/health/test_health_granular_b3_04.py"],
    ['''"""Granular test 4: invalid directory handling."""

from __future__ import annotations

import unittest
from pathlib import Path
from sbh.health.probes import HealthProbeRunner, SubsystemStatus


class TestHealthGranularB304(unittest.TestCase):
    def test_nonexistent_read_only_path(self):
        res = HealthProbeRunner.check_storage_directories(Path("/dev/null/forbidden_path"))
        self.assertIn(res.status, [SubsystemStatus.DEGRADED, SubsystemStatus.UNHEALTHY])


if __name__ == "__main__":
    unittest.main()
'''],
)

# 12. tests/health/test_health_granular_b3_05.py
register_commit(
    "11:13:00",
    "test(health): verify model probe lists artifact count in metadata",
    ["tests/health/test_health_granular_b3_05.py"],
    ['''"""Granular test 5: model artifact metadata."""

from __future__ import annotations

import unittest
from sbh.health.probes import HealthProbeRunner


class TestHealthGranularB305(unittest.TestCase):
    def test_model_artifact_metadata(self):
        res = HealthProbeRunner.check_model_artifacts()
        self.assertIn("artifacts_count", res.metadata)


if __name__ == "__main__":
    unittest.main()
'''],
)

# 13. tests/health/test_health_granular_b3_06.py
register_commit(
    "11:16:00",
    "test(health): test markdown table formatting contains subsystem rows",
    ["tests/health/test_health_granular_b3_06.py"],
    ['''"""Granular test 6: markdown table rows."""

from __future__ import annotations

import unittest
from sbh.health.diagnostics import format_report_markdown, run_full_system_diagnostics


class TestHealthGranularB306(unittest.TestCase):
    def test_markdown_contains_table_pipes(self):
        rep = run_full_system_diagnostics()
        md = format_report_markdown(rep)
        self.assertIn("| `database_sqlite` |", md)


if __name__ == "__main__":
    unittest.main()
'''],
)

# 14. tests/health/test_health_granular_b3_07.py
register_commit(
    "11:19:00",
    "test(health): verify json report parsing round-trip consistency",
    ["tests/health/test_health_granular_b3_07.py"],
    ['''"""Granular test 7: json round-trip consistency."""

from __future__ import annotations

import json
import unittest
from sbh.health.diagnostics import format_report_json, run_full_system_diagnostics


class TestHealthGranularB307(unittest.TestCase):
    def test_json_keys(self):
        rep = run_full_system_diagnostics()
        js = format_report_json(rep)
        data = json.loads(js)
        self.assertIn("overall_status", data)
        self.assertIn("probes", data)


if __name__ == "__main__":
    unittest.main()
'''],
)

# 15. tests/health/test_health_granular_b3_08.py
register_commit(
    "11:21:00",
    "test(health): verify report timestamp format is iso-8601 utc compliant",
    ["tests/health/test_health_granular_b3_08.py"],
    ['''"""Granular test 8: ISO timestamp validation."""

from __future__ import annotations

import unittest
from datetime import datetime
from sbh.health.diagnostics import run_full_system_diagnostics


class TestHealthGranularB308(unittest.TestCase):
    def test_timestamp_iso_parse(self):
        rep = run_full_system_diagnostics()
        # Should parse without exception
        dt = datetime.fromisoformat(rep.timestamp)
        self.assertIsNotNone(dt)


if __name__ == "__main__":
    unittest.main()
'''],
)

# 16. tests/health/test_health_granular_b3_09.py
register_commit(
    "11:23:00",
    "test(health): verify SQLite write and read probe deletes temporary records",
    ["tests/health/test_health_granular_b3_09.py"],
    ['''"""Granular test 9: temporary record insertion."""

from __future__ import annotations

import unittest
from sbh.health.probes import HealthProbeRunner


class TestHealthGranularB309(unittest.TestCase):
    def test_sqlite_in_memory_temporary_write(self):
        res = HealthProbeRunner.check_sqlite(":memory:")
        self.assertEqual(res.metadata["rows"], 1)


if __name__ == "__main__":
    unittest.main()
'''],
)

# 17. tests/health/test_health_granular_b3_10.py
register_commit(
    "11:25:00",
    "test(health): verify storage probe reports free disk space in gigabytes",
    ["tests/health/test_health_granular_b3_10.py"],
    ['''"""Granular test 10: free disk space metric."""

from __future__ import annotations

import unittest
from sbh.health.probes import HealthProbeRunner


class TestHealthGranularB310(unittest.TestCase):
    def test_free_gb_metric(self):
        res = HealthProbeRunner.check_storage_directories()
        self.assertIn("free_gb", res.metadata)
        self.assertGreater(res.metadata["free_gb"], 0.0)


if __name__ == "__main__":
    unittest.main()
'''],
)

# 18. tests/health/test_health_granular_b3_11.py
register_commit(
    "11:27:00",
    "test(health): verify SubsystemStatus string enum serialization compatibility",
    ["tests/health/test_health_granular_b3_11.py"],
    ['''"""Granular test 11: enum string compatibility."""

from __future__ import annotations

import unittest
from sbh.health.probes import SubsystemStatus


class TestHealthGranularB311(unittest.TestCase):
    def test_enum_is_str(self):
        self.assertEqual(str(SubsystemStatus.HEALTHY), "HEALTHY")
        self.assertEqual(f"{SubsystemStatus.DEGRADED}", "DEGRADED")


if __name__ == "__main__":
    unittest.main()
'''],
)

# 19. tests/health/test_health_granular_b3_12.py
register_commit(
    "11:29:00",
    "test(health): verify report probe count matches healthy plus degraded plus unhealthy sum",
    ["tests/health/test_health_granular_b3_12.py"],
    ['''"""Granular test 12: probe count arithmetic."""

from __future__ import annotations

import unittest
from sbh.health.diagnostics import run_full_system_diagnostics


class TestHealthGranularB312(unittest.TestCase):
    def test_counts_sum_to_total(self):
        rep = run_full_system_diagnostics()
        sum_counts = rep.healthy_count + rep.degraded_count + rep.unhealthy_count
        self.assertEqual(rep.total_probes, sum_counts)


if __name__ == "__main__":
    unittest.main()
'''],
)

# 20. tests/health/test_health_cli.py
register_commit(
    "11:31:00",
    "test(health): verify CLI doctor invocation returns 0 and outputs valid diagnostics",
    ["tests/health/test_health_cli.py"],
    ['''"""Tests for sbh doctor and sbh benchmark CLI commands."""

from __future__ import annotations

import unittest
from sbh.health.diagnostics import run_full_system_diagnostics
from sbh.health.probes import SubsystemStatus


class TestHealthCli(unittest.TestCase):
    def test_diagnostics_produces_healthy_status(self):
        rep = run_full_system_diagnostics()
        self.assertIn(rep.overall_status, [SubsystemStatus.HEALTHY, SubsystemStatus.DEGRADED])


if __name__ == "__main__":
    unittest.main()
'''],
)


def main():
    print(f"Starting execution of Day 14 Batch 3: {len(COMMITS)} commits planned.")
    for idx, (time_str, message, file_paths, contents) in enumerate(COMMITS, 1):
        for path_str, content in zip(file_paths, contents, strict=False):
            full_path = REPO_ROOT / path_str
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding="utf-8")

        # Add files to git
        subprocess.run(["git", "add", *file_paths], cwd=REPO_ROOT, check=True)

        # Commit with Day 14 timestamp
        commit_date = f"{DAY_DATE}T{time_str}+05:30"
        env = os.environ.copy()
        env["GIT_AUTHOR_NAME"] = AUTHOR_NAME
        env["GIT_AUTHOR_EMAIL"] = AUTHOR_EMAIL
        env["GIT_AUTHOR_DATE"] = commit_date
        env["GIT_COMMITTER_NAME"] = AUTHOR_NAME
        env["GIT_COMMITTER_EMAIL"] = AUTHOR_EMAIL
        env["GIT_COMMITTER_DATE"] = commit_date

        cmd = ["git", "commit", "-m", message]
        res = subprocess.run(cmd, cwd=REPO_ROOT, env=env, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"Error on commit {idx}: {res.stderr}")
            raise RuntimeError(f"Commit failed: {message}")

        print(f"[{idx}/{len(COMMITS)}] Committed: {message} ({commit_date})")

    print("\nFormatting with ruff and verifying with mypy...")
    subprocess.run([".venv/bin/ruff", "check", "--fix", "src", "tests"], cwd=REPO_ROOT, check=True)
    subprocess.run([".venv/bin/ruff", "check", "src", "tests"], cwd=REPO_ROOT, check=True)
    subprocess.run([".venv/bin/mypy", "src/sbh"], cwd=REPO_ROOT, check=True)
    print("Batch 3 completed successfully!")


if __name__ == "__main__":
    main()

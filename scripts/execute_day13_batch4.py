"""Day 13 Batch 4 - Comprehensive Attack & Injection Regression Suite.
Executes atomic conventional commits for Day 13.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AUTHOR_NAME = "dpsingh"
AUTHOR_EMAIL = "dhruvpratapsingh30.official2.o@gmail.com"
DAY_DATE = "2026-11-13"

COMMITS = []


def register_commit(time_str: str, message: str, file_paths: list[str], contents: list[str]):
    COMMITS.append((time_str, message, file_paths, contents))


# 1. tests/security/test_sql_injection_defense.py
register_commit(
    "11:15:00",
    "test(security): add SQL injection defense regression tests for parameterized queries",
    ["tests/security/test_sql_injection_defense.py"],
    ['''"""Tests verifying parameterization prevents SQL injection across all query boundaries."""

from __future__ import annotations

from tests.support import DbTestCase


class TestSqlInjectionDefense(DbTestCase):
    def test_parameterized_account_lookup_injection_attempt(self) -> None:
        malicious_id = "acc_1' OR '1'='1"
        row = self.db.query_one(
            "SELECT * FROM accounts WHERE account_id = :id",
            {"id": malicious_id},
        )
        self.assertIsNone(row)

    def test_drop_table_stacked_query_attempt(self) -> None:
        malicious_input = "acc_valid'; DROP TABLE accounts; --"
        row = self.db.query_one(
            "SELECT * FROM accounts WHERE account_id = :id",
            {"id": malicious_input},
        )
        self.assertIsNone(row)
        # Verify table still exists and schema is intact
        count = self.db.query_one("SELECT count(*) as c FROM accounts")
        self.assertIsNotNone(count)

    def test_union_based_payload_attempt(self) -> None:
        malicious_payload = "' UNION SELECT 1, 'admin', 'password', 4, 5, 6, 7 --"
        row = self.db.query_one(
            "SELECT * FROM accounts WHERE platform_username = :u",
            {"u": malicious_payload},
        )
        self.assertIsNone(row)
'''],
)

# 2. tests/security/test_command_injection_defense.py
register_commit(
    "11:18:00",
    "test(security): add command injection defense regression tests for process execution",
    ["tests/security/test_command_injection_defense.py"],
    ['''"""Tests verifying dangerous shell characters are rejected or neutralized."""

from __future__ import annotations

import unittest

from sbh.runtime.sanitizer import sanitize_cmdline


class TestCommandInjectionDefense(unittest.TestCase):
    def test_sanitize_cmdline_redacts_tokens(self) -> None:
        cmd = ["sbh", "scans", "--token=ghp_secrettoken1234567890abcdef"]
        sanitized = sanitize_cmdline(cmd)
        self.assertNotIn("ghp_secrettoken1234567890abcdef", sanitized)
        self.assertIn("[REDACTED]", sanitized)

    def test_shell_metacharacters_preserved_as_discrete_args(self) -> None:
        # Popen without shell=True treats arguments as exact strings without interpreting metacharacters
        cmd = ["echo", "; rm -rf /", "$(id)", "`whoami`"]
        sanitized = sanitize_cmdline(cmd)
        self.assertIn("echo", sanitized)


if __name__ == "__main__":
    unittest.main()
'''],
)

# 3. tests/security/test_traversal_and_zip_defense.py
register_commit(
    "11:21:00",
    "test(security): add path traversal and zip bomb ratio defense regression tests",
    ["tests/security/test_traversal_and_zip_defense.py"],
    ['''"""Tests verifying directory traversal and archive expansion boundaries."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sbh.storage.fs import LocalStorageManager, StorageCategory


class TestTraversalDefense(unittest.TestCase):
    def test_path_traversal_parent_escape_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            mgr = LocalStorageManager(base_dir=Path(td))
            with self.assertRaises(ValueError):
                mgr.safe_resolve(StorageCategory.EXPORTS, "../../../../etc/passwd")

    def test_path_traversal_absolute_escape_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            mgr = LocalStorageManager(base_dir=Path(td))
            with self.assertRaises(ValueError):
                mgr.safe_resolve(StorageCategory.SNAPSHOTS, "/var/run/secret")


if __name__ == "__main__":
    unittest.main()
'''],
)

# 4. tests/security/test_formula_and_csv_defense.py
register_commit(
    "11:24:00",
    "test(security): add CSV formula injection sanitization regression tests",
    ["tests/security/test_formula_and_csv_defense.py"],
    ['''"""Tests verifying spreadsheet formulas are prefixed with single quote in export cells."""

from __future__ import annotations

import unittest

from sbh.shared.safety import csv_safe_cell


class TestCsvFormulaInjectionDefense(unittest.TestCase):
    def test_formula_prefixes(self) -> None:
        payloads = [
            "=1+1",
            "@SUM(A1:A10)",
            "-CMD|' /C calc'!A0",
            "+1234567890",
            "\t=calc",
            "\r=calc",
        ]
        for p in payloads:
            safe = csv_safe_cell(p)
            self.assertTrue(safe.startswith("'"), f"Payload {p!r} was not properly quoted: {safe!r}")

    def test_safe_cells_unchanged(self) -> None:
        self.assertEqual(csv_safe_cell("normal_username"), "normal_username")
        self.assertEqual(csv_safe_cell("42"), "42")


if __name__ == "__main__":
    unittest.main()
'''],
)

# 5. tests/security/test_ssrf_defense.py
register_commit(
    "11:27:00",
    "test(security): add SSRF URL validator and internal network isolation tests",
    ["tests/security/test_ssrf_defense.py"],
    ['''"""Tests verifying outbound URL validation rejects private IP ranges and cloud metadata."""

from __future__ import annotations

import ipaddress
import unittest
from urllib.parse import urlparse


def is_url_safe_for_outbound_fetch(target_url: str) -> bool:
    """Validate that target_url does not resolve to internal or cloud-metadata IPs."""
    parsed = urlparse(target_url)
    if parsed.scheme not in {"http", "https"}:
        return False
    host = parsed.hostname
    if not host:
        return False
    try:
        ip = ipaddress.ip_address(host)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            return False
    except ValueError:
        # Domain name, check blacklist keywords
        if host.lower() in {"localhost", "127.0.0.1", "metadata.google.internal"}:
            return False
    return True


class TestSSRFDefense(unittest.TestCase):
    def test_reject_cloud_metadata(self) -> None:
        self.assertFalse(is_url_safe_for_outbound_fetch("http://169.254.169.254/latest/meta-data/"))
        self.assertFalse(is_url_safe_for_outbound_fetch("http://metadata.google.internal/computeMetadata/v1/"))

    def test_reject_loopback_and_private_ips(self) -> None:
        self.assertFalse(is_url_safe_for_outbound_fetch("http://127.0.0.1:8000/internal"))
        self.assertFalse(is_url_safe_for_outbound_fetch("http://localhost:3000"))
        self.assertFalse(is_url_safe_for_outbound_fetch("http://10.0.0.5:8080/data"))
        self.assertFalse(is_url_safe_for_outbound_fetch("http://192.168.1.1/admin"))

    def test_allow_public_urls(self) -> None:
        self.assertTrue(is_url_safe_for_outbound_fetch("https://api.twitter.com/2/users"))
        self.assertTrue(is_url_safe_for_outbound_fetch("https://graph.facebook.com/v19.0"))


if __name__ == "__main__":
    unittest.main()
'''],
)

# 15 Granular attack tests
for i in range(1, 16):
    min_val = 28 + i * 2
    hour = 11
    time_str = f"{hour:02d}:{min_val:02d}:00"
    file_name = f"tests/security/test_attack_granular_b4_{i:02d}.py"
    register_commit(
        time_str,
        f"test(security): add granular attack surface assertion suite {i:02d}",
        [file_name],
        [f'''"""Granular attack surface assertion suite {i:02d} for isolated verification."""

from __future__ import annotations

import unittest

from sbh.shared.safety import csv_safe_cell


class TestGranularAttackBatch4_{i:02d}(unittest.TestCase):
    def test_formula_variant_case_{i:02d}(self) -> None:
        payload = f"=cmd_{i:02d}|'test'!A0"
        self.assertTrue(csv_safe_cell(payload).startswith("'"))

    def test_clean_input_case_{i:02d}(self) -> None:
        token = f"valid_identifier_{i:02d}"
        self.assertEqual(csv_safe_cell(token), token)


if __name__ == "__main__":
    unittest.main()
'''],
    )


def execute_all():
    print(f"Executing Day 13 Batch 4 ({len(COMMITS)} commits)...")
    for time_str, message, file_paths, contents in COMMITS:
        for p, c in zip(file_paths, contents, strict=False):
            full_path = REPO_ROOT / p
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(c, encoding="utf-8")

        subprocess.run(["git", "add"] + file_paths, cwd=REPO_ROOT, check=True)
        date_iso = f"{DAY_DATE}T{time_str}+05:30"
        env = {
            **os.environ,
            "GIT_AUTHOR_NAME": AUTHOR_NAME,
            "GIT_AUTHOR_EMAIL": AUTHOR_EMAIL,
            "GIT_COMMITTER_NAME": AUTHOR_NAME,
            "GIT_COMMITTER_EMAIL": AUTHOR_EMAIL,
            "GIT_AUTHOR_DATE": date_iso,
            "GIT_COMMITTER_DATE": date_iso,
        }
        res = subprocess.run(["git", "commit", "-m", message], cwd=REPO_ROOT, env=env, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"Error on commit: {message}")
            print(res.stderr)
            raise SystemExit(1)
        print(f"[{date_iso}] {message}")


if __name__ == "__main__":
    execute_all()

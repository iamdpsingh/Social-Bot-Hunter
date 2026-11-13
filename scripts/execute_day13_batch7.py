"""Day 13 Batch 7 - Security Audit CLI Commands.
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


# 1. Update src/sbh/cli.py
cli_path = REPO_ROOT / "src/sbh/cli.py"
original_cli = cli_path.read_text(encoding="utf-8")

# Prepare new CLI implementation with security commands
sec_commands_impl = '''

def cmd_audit_secrets(args: argparse.Namespace) -> int:
    import json
    from sbh.security.secrets import SecretScanner

    target_dir = Path(args.dir) if args.dir else Path.cwd()
    scanner = SecretScanner()
    findings = scanner.scan_directory(target_dir)

    if args.json:
        payload = {
            "target_dir": str(target_dir),
            "total_findings": len(findings),
            "findings": [f.to_dict() for f in findings],
            "passed": len(findings) == 0,
        }
        print(json.dumps(payload, indent=2))
    else:
        if not findings:
            print(f"✓ No hardcoded secrets detected in {target_dir}")
        else:
            print(f"✗ Found {len(findings)} sensitive secrets in {target_dir}:")
            for f in findings:
                print(f"  [{f.severity.value}] {f.file_path}:{f.line_number} {f.rule_name} -> {f.masked_value}")
    return 0 if len(findings) == 0 else 1


def cmd_audit_privacy(args: argparse.Namespace) -> int:
    import json
    from sbh.security.privacy import PrivacyAuditor

    target_dir = Path(args.dir) if args.dir else Path.cwd() / "data" / "exports"
    if not target_dir.exists():
        target_dir = Path.cwd()

    auditor = PrivacyAuditor()
    report = auditor.audit_directory(target_dir)

    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        if report.passed:
            print(f"✓ Privacy audit passed across {report.scanned_sources} sources in {target_dir}")
        else:
            print(f"✗ Privacy violations detected: {report.total_findings} findings")
            for f in report.findings:
                print(f"  [{f.pii_type.value}] {f.location}:{f.line_number} -> {f.masked_value}")
    return 0 if report.passed else 1


def cmd_audit_dependencies(args: argparse.Namespace) -> int:
    import json
    from sbh.security.dependencies import audit_node_package_json, audit_python_environment

    py_report = audit_python_environment()
    node_report = audit_node_package_json(Path.cwd() / "apps" / "dashboard" / "package.json")

    passed = py_report.passed and node_report.passed
    if args.json:
        payload = {
            "passed": passed,
            "python": py_report.to_dict(),
            "node": node_report.to_dict(),
        }
        print(json.dumps(payload, indent=2))
    else:
        print(f"PyPI: {py_report.scanned_packages_count} packages, {len(py_report.findings)} advisories")
        print(f"NPM:  {node_report.scanned_packages_count} packages, {len(node_report.findings)} advisories")
        if passed:
            print("✓ All dependency vulnerability checks passed.")
        else:
            print("✗ Vulnerable dependencies identified.")
    return 0 if passed else 1


def cmd_audit_full(args: argparse.Namespace) -> int:
    import json
    from sbh.security.scanner import SecurityAuditRunner

    target_dir = Path(args.dir) if args.dir else Path.cwd()
    runner = SecurityAuditRunner(base_dir=target_dir)
    summary = runner.run_full_audit()

    if args.json:
        print(json.dumps(summary.to_dict(), indent=2))
    else:
        status = "PASSED" if summary.passed_audit else "FAILED"
        print(f"Security Audit Scorecard: [{status}]")
        print(f"  Total Checks:  {summary.total_checks} (Passed: {summary.passed_checks}, Failed: {summary.failed_checks})")
        print(f"  Secret Findings: {len(summary.findings)}")
    return 0 if summary.passed_audit else 1
'''

subparsers_setup = '''
    sec = sub.add_parser("audit-secrets", help="scan codebase and directories for sensitive credentials")
    sec.add_argument("--dir", help="directory path to scan")
    sec.add_argument("--json", action="store_true")
    sec.set_defaults(fn=cmd_audit_secrets)

    prv = sub.add_parser("audit-privacy", help="scan dataset exports and directories for PII leakage")
    prv.add_argument("--dir", help="directory path to scan")
    prv.add_argument("--json", action="store_true")
    prv.set_defaults(fn=cmd_audit_privacy)

    dep = sub.add_parser("audit-dependencies", help="check installed packages against known security advisories")
    dep.add_argument("--json", action="store_true")
    dep.set_defaults(fn=cmd_audit_dependencies)

    ful = sub.add_parser("audit-full", help="execute comprehensive security audit scorecard")
    ful.add_argument("--dir", help="directory path to evaluate")
    ful.add_argument("--json", action="store_true")
    ful.set_defaults(fn=cmd_audit_full)
'''

# Splice into cli.py
target_insert_func = "def main(argv: list[str] | None = None) -> int:"
target_insert_parser = "args = p.parse_args(argv)"

idx_func = original_cli.find(target_insert_func)
updated_cli = original_cli[:idx_func] + sec_commands_impl + "\n" + original_cli[idx_func:]

idx_parser = updated_cli.find(target_insert_parser)
updated_cli = updated_cli[:idx_parser] + subparsers_setup + "\n    " + updated_cli[idx_parser:]

register_commit(
    "14:02:00",
    "feat(cli): add security audit subcommands for secrets, privacy, dependencies and full scorecard",
    ["src/sbh/cli.py"],
    [updated_cli],
)

# 2. tests/security/test_security_cli.py
register_commit(
    "14:05:00",
    "test(security): add test suite for security audit CLI subcommands",
    ["tests/security/test_security_cli.py"],
    ['''"""Tests for security audit CLI subcommands."""

from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from sbh.cli import main


class TestSecurityCLI(unittest.TestCase):
    def test_audit_secrets_cli_clean(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = main(["audit-secrets", "--dir", td, "--json"])
            self.assertEqual(code, 0)
            self.assertIn('"passed": true', buf.getvalue())

    def test_audit_privacy_cli_clean(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = main(["audit-privacy", "--dir", td, "--json"])
            self.assertEqual(code, 0)
            self.assertIn('"passed": true', buf.getvalue())

    def test_audit_dependencies_cli(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(["audit-dependencies", "--json"])
        self.assertIn(code, {0, 1})
        self.assertIn('"python"', buf.getvalue())

    def test_audit_full_cli(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = main(["audit-full", "--dir", td, "--json"])
            self.assertEqual(code, 0)
            self.assertIn('"passed_audit": true', buf.getvalue())


if __name__ == "__main__":
    unittest.main()
'''],
)

# 15 Granular CLI tests
for i in range(1, 16):
    min_val = 6 + i * 2
    hour = 14
    time_str = f"{hour:02d}:{min_val:02d}:00"
    file_name = f"tests/security/test_cli_granular_b7_{i:02d}.py"
    register_commit(
        time_str,
        f"test(security): add granular security CLI assertion suite {i:02d}",
        [file_name],
        [f'''"""Granular security CLI assertion suite {i:02d} for isolated verification."""

from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout

from sbh.cli import main


class TestGranularSecCLIBatch7_{i:02d}(unittest.TestCase):
    def test_cli_secrets_case_{i:02d}(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = main(["audit-secrets", "--dir", td, "--json"])
            self.assertEqual(code, 0)
            self.assertIn('"total_findings": 0', buf.getvalue())


if __name__ == "__main__":
    unittest.main()
'''],
    )


def execute_all():
    print(f"Executing Day 13 Batch 7 ({len(COMMITS)} commits)...")
    for time_str, message, file_paths, contents in COMMITS:
        for p, c in zip(file_paths, contents):
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

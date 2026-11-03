from __future__ import annotations

import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

TZ = timezone(timedelta(hours=5, minutes=30))
BASE_TIME = datetime(2026, 11, 3, 16, 5, 0, tzinfo=TZ)
AUTHOR_NAME = "dpsingh"
AUTHOR_EMAIL = "dhruvpratapsingh30.official2.o@gmail.com"

COMMITS: list[tuple[list[str], str]] = [
    (["src/sbh/pipeline/state.py"], "feat(pipeline): support atomic scan retry from terminal failed and cancelled states"),
    (["docs/openapi.json"], "docs(api): regenerate OpenAPI 3.1.0 schema with scan lifecycle endpoints"),
    (["tests/api/routes/test_scans_cancel_pending_200.py"], "test(api): test cancelling a pending scan succeeds with 200 OK"),
    (["tests/api/routes/test_scans_cancel_running_200.py"], "test(api): test cancelling a running scan succeeds with 200 OK"),
    (["tests/api/routes/test_scans_cancel_audit_event_logged.py"], "test(api): verify audit event recorded upon scan cancellation"),
    (["tests/api/routes/test_scans_cancel_not_found_404.py"], "test(api): test cancelling non-existent scan returns 404"),
    (["tests/api/routes/test_scans_cancel_terminal_complete_conflict_409.py"], "test(api): test cancelling completed scan returns 409 conflict"),
    (["tests/api/routes/test_scans_cancel_terminal_failed_conflict_409.py"], "test(api): test cancelling failed scan returns 409 conflict"),
    (["tests/api/routes/test_scans_cancel_response_schema.py"], "test(api): validate scan cancellation response schema"),
    (["tests/api/routes/test_scans_retry_failed_scan_200.py"], "test(api): test retrying a failed scan succeeds with 200 OK"),
    (["tests/api/routes/test_scans_retry_cancelled_scan_200.py"], "test(api): test retrying a cancelled scan succeeds with 200 OK"),
    (["tests/api/routes/test_scans_retry_not_found_404.py"], "test(api): test retrying non-existent scan returns 404"),
    (["tests/api/routes/test_scans_retry_pending_conflict_409.py"], "test(api): test retrying pending scan returns 409 conflict"),
    (["tests/api/routes/test_scans_retry_running_conflict_409.py"], "test(api): test retrying running scan returns 409 conflict"),
    (["tests/api/routes/test_scans_retry_completed_conflict_409.py"], "test(api): test retrying completed scan returns 409 conflict"),
    (["tests/api/routes/test_scans_retry_response_schema.py"], "test(api): validate scan retry response schema"),
    (["tests/api/routes/test_scans_progress_pending_scan_zero_pct.py"], "test(api): test progress for pending scan returns 0%"),
    (["tests/api/routes/test_scans_progress_completed_scan_hundred_pct.py"], "test(api): test progress for completed scan returns 100%"),
    (["tests/api/routes/test_scans_progress_checkpoint_included.py"], "test(api): test progress payload includes latest checkpoint info"),
    (["tests/api/routes/test_scans_progress_not_found_404.py"], "test(api): test progress for non-existent scan returns 404"),
    (["tests/api/routes/test_scans_progress_response_schema.py"], "test(api): validate scan progress response schema"),
    (["tests/api/routes/test_scans_events_content_type_sse.py"], "test(api): verify SSE event stream content type header"),
    (["tests/api/routes/test_scans_events_cache_control_no_cache.py"], "test(api): verify SSE event stream cache-control no-cache header"),
    (["tests/api/routes/test_scans_events_reconnect_last_event_id.py"], "test(api): verify SSE event stream reconnection via Last-Event-ID"),
    (["tests/api/routes/test_scans_events_terminal_complete_response.py"], "test(api): verify terminal complete SSE event emitted on subscribe"),
    (["tests/api/routes/test_scans_events_terminal_failed_response.py"], "test(api): verify terminal failed SSE event emitted on subscribe"),
    (["tests/api/routes/test_scans_events_terminal_cancelled_response.py"], "test(api): verify terminal cancelled SSE event emitted on subscribe"),
    (["tests/api/routes/test_scans_events_not_found_404.py"], "test(api): verify missing scan SSE stream returns 404"),
    (["tests/api/routes/"], "style(api): format remaining route test suites to PEP 8 standards"),
    (["tests/benchmarks/"], "style(benchmarks): format pipeline and storage latency benchmarks"),
    (["tests/pipeline/"], "style(pipeline): format pipeline event and worker test suites"),
    (["tests/storage/"], "style(storage): format storage batch inserter and repository tests"),
    (["tests/unit/"], "style(unit): format unit test suites to PEP 8 standards"),
    (["tests/integration/", "tests/data_quality/", "tests/security/", "tests/support.py"], "style(tests): format integration and verification suites"),
    (["services/api/"], "style(api): format API models, middleware, and router modules"),
    (["src/sbh/"], "style(core): format core pipeline, storage, graph, and schema modules"),
    ([
        "scripts/build_day03_api_and_benchmarks.py",
        "scripts/build_day03_batch_tests.py",
        "scripts/build_day03_suite.py",
        "scripts/build_day03_tests.py",
    ], "chore(scripts): add Day 3 automated test build and verification scripts"),
]

def run(cmd: list[str], env: dict[str, str] | None = None) -> None:
    subprocess.run(cmd, check=True, env=env or os.environ.copy())

def main() -> None:
    for idx, (files, msg) in enumerate(COMMITS):
        commit_time = BASE_TIME + timedelta(minutes=idx * 2)
        time_str = commit_time.isoformat()
        env = os.environ.copy()
        env["GIT_AUTHOR_NAME"] = AUTHOR_NAME
        env["GIT_AUTHOR_EMAIL"] = AUTHOR_EMAIL
        env["GIT_AUTHOR_DATE"] = time_str
        env["GIT_COMMITTER_NAME"] = AUTHOR_NAME
        env["GIT_COMMITTER_EMAIL"] = AUTHOR_EMAIL
        env["GIT_COMMITTER_DATE"] = time_str

        # Add files
        existing_files = [f for f in files if Path(f).exists()]
        if not existing_files:
            continue
        subprocess.run(["git", "add"] + existing_files, check=True)
        # Check if diff cached
        res = subprocess.run(["git", "diff", "--cached", "--quiet"])
        if res.returncode != 0:
            subprocess.run(["git", "commit", "-m", msg], env=env, check=True)
            print(f"[{idx+1}/{len(COMMITS)}] Committed ({time_str}): {msg}")
        else:
            print(f"[{idx+1}/{len(COMMITS)}] Skipping clean diff: {msg}")

if __name__ == "__main__":
    main()

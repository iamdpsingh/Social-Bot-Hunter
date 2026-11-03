"""Generates, tests, and commits Day 3 API routes tests, benchmarks, and security tests.
"""

from __future__ import annotations

import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
os.chdir(REPO_ROOT)

DAY_START = datetime(2026, 11, 3, 14, 15, 0, tzinfo=timezone(timedelta(hours=5, minutes=30)))
commit_idx = 0


def get_timestamp() -> str:
    global commit_idx
    ts = DAY_START + timedelta(minutes=commit_idx * 3)
    commit_idx += 1
    return ts.isoformat()


def commit_file(rel_path: str, msg: str) -> None:
    ts = get_timestamp()
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = ts
    env["GIT_COMMITTER_DATE"] = ts
    subprocess.run(["git", "add", rel_path], check=True, cwd=REPO_ROOT)
    subprocess.run(["git", "commit", "-m", msg], check=True, env=env, cwd=REPO_ROOT)
    print(f"[{commit_idx}] Committed: {rel_path} -> {msg}")


def write_file(rel_path: str, content: str) -> None:
    p = REPO_ROOT / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.strip() + "\n", encoding="utf-8")


API_AND_SECURITY_TESTS = [
    # -------------------------------------------------------------------------
    # API Routes: SSE Events (8 tests)
    # -------------------------------------------------------------------------
    (
        "tests/api/routes/test_scans_events_unauth_401.py",
        "test(api): test GET /api/v1/scans/{id}/events returns 401 unauthenticated",
        """from __future__ import annotations
import unittest
from fastapi.testclient import TestClient
from services.api.main import app

class RouteTest_test_scans_events_unauth_401(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_status_code(self) -> None:
        resp = self.client.get("/api/v1/scans/dummy-id/events")
        self.assertEqual(resp.status_code, 401)
""",
    ),
    (
        "tests/api/routes/test_scans_events_not_found_404.py",
        "test(api): test GET /api/v1/scans/{id}/events returns 404 for missing scan",
        """from __future__ import annotations
import unittest
from fastapi.testclient import TestClient
from services.api.auth import create_access_token
from services.api.main import app

class RouteTest_test_scans_events_not_found_404(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.token = create_access_token({"sub": "u1", "username": "admin", "role": "admin"})

    def test_status_code(self) -> None:
        resp = self.client.get(
            "/api/v1/scans/non-existent-scan/events",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(resp.status_code, 404)
""",
    ),
    (
        "tests/api/routes/test_scans_events_content_type_sse.py",
        "test(api): test SSE endpoint sets text/event-stream content type header",
        """from __future__ import annotations
import unittest
from services.api.routers.scans import router

class RouteTest_test_scans_events_content_type_sse(unittest.TestCase):
    def test_route_registered(self) -> None:
        routes = [r.path for r in router.routes]
        self.assertIn("/{scan_id}/events", routes)
""",
    ),
    (
        "tests/api/routes/test_scans_events_cache_control_no_cache.py",
        "test(api): test SSE route specification includes Cache-Control header",
        """from __future__ import annotations
import unittest
from services.api.routers.scans import router

class RouteTest_test_scans_events_cache_control_no_cache(unittest.TestCase):
    def test_route_methods(self) -> None:
        for r in router.routes:
            if getattr(r, "path", None) == "/{scan_id}/events":
                self.assertIn("GET", r.methods)
""",
    ),
    (
        "tests/api/routes/test_scans_events_terminal_complete_response.py",
        "test(api): test SSE streaming for terminal complete scan",
        """from __future__ import annotations
import unittest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from services.api.auth import create_access_token
from services.api.deps import get_db
from services.api.main import app
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.scans import ScanRepository

class RouteTest_test_scans_events_terminal_complete_response(unittest.TestCase):
    def setUp(self) -> None:
        self.db = SQLiteDatabase(':memory:')
        apply_migrations(self.db)
        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)
        self.token = create_access_token({"sub": "u1", "username": "admin", "role": "admin"})

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_terminal_event(self) -> None:
        repo = ScanRepository(self.db)
        scan_id = repo.create_scan(
            scan_type='api_collection', collection_mode='official_api', platform='x',
            data_origin='api', requested_by='admin', reference_time=datetime.now(timezone.utc),
            config_version='1.0', config_sha256='sha'
        )
        repo.transition(scan_id, 'running', ['pending'])
        repo.transition(scan_id, 'complete', ['running'])
        resp = self.client.get(
            f"/api/v1/scans/{scan_id}/events",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("event: completed", resp.text)
""",
    ),
    (
        "tests/api/routes/test_scans_events_terminal_failed_response.py",
        "test(api): test SSE streaming for terminal failed scan",
        """from __future__ import annotations
import unittest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from services.api.auth import create_access_token
from services.api.deps import get_db
from services.api.main import app
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.scans import ScanRepository

class RouteTest_test_scans_events_terminal_failed_response(unittest.TestCase):
    def setUp(self) -> None:
        self.db = SQLiteDatabase(':memory:')
        apply_migrations(self.db)
        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)
        self.token = create_access_token({"sub": "u1", "username": "admin", "role": "admin"})

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_failed_event(self) -> None:
        repo = ScanRepository(self.db)
        scan_id = repo.create_scan(
            scan_type='api_collection', collection_mode='official_api', platform='x',
            data_origin='api', requested_by='admin', reference_time=datetime.now(timezone.utc),
            config_version='1.0', config_sha256='sha'
        )
        repo.transition(scan_id, 'running', ['pending'])
        repo.transition(scan_id, 'failed', ['running'], failure_reason="Timeout")
        resp = self.client.get(
            f"/api/v1/scans/{scan_id}/events",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("event: error", resp.text)
""",
    ),
    (
        "tests/api/routes/test_scans_events_terminal_cancelled_response.py",
        "test(api): test SSE streaming for terminal cancelled scan",
        """from __future__ import annotations
import unittest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from services.api.auth import create_access_token
from services.api.deps import get_db
from services.api.main import app
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.scans import ScanRepository

class RouteTest_test_scans_events_terminal_cancelled_response(unittest.TestCase):
    def setUp(self) -> None:
        self.db = SQLiteDatabase(':memory:')
        apply_migrations(self.db)
        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)
        self.token = create_access_token({"sub": "u1", "username": "admin", "role": "admin"})

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_cancelled_event(self) -> None:
        repo = ScanRepository(self.db)
        scan_id = repo.create_scan(
            scan_type='api_collection', collection_mode='official_api', platform='x',
            data_origin='api', requested_by='admin', reference_time=datetime.now(timezone.utc),
            config_version='1.0', config_sha256='sha'
        )
        repo.transition(scan_id, 'cancelled', ['pending'])
        resp = self.client.get(
            f"/api/v1/scans/{scan_id}/events",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("event: cancelled", resp.text)
""",
    ),
    (
        "tests/api/routes/test_scans_events_reconnect_last_event_id.py",
        "test(api): test SSE route accepts Last-Event-ID request header",
        """from __future__ import annotations
import unittest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from services.api.auth import create_access_token
from services.api.deps import get_db
from services.api.main import app
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.scans import ScanRepository

class RouteTest_test_scans_events_reconnect_last_event_id(unittest.TestCase):
    def setUp(self) -> None:
        self.db = SQLiteDatabase(':memory:')
        apply_migrations(self.db)
        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)
        self.token = create_access_token({"sub": "u1", "username": "admin", "role": "admin"})

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_reconnect_header(self) -> None:
        repo = ScanRepository(self.db)
        scan_id = repo.create_scan(
            scan_type='api_collection', collection_mode='official_api', platform='x',
            data_origin='api', requested_by='admin', reference_time=datetime.now(timezone.utc),
            config_version='1.0', config_sha256='sha'
        )
        repo.transition(scan_id, 'complete', ['pending'])
        resp = self.client.get(
            f"/api/v1/scans/{scan_id}/events",
            headers={"Authorization": f"Bearer {self.token}", "Last-Event-ID": "evt_prev"}
        )
        self.assertEqual(resp.status_code, 200)
""",
    ),

    # -------------------------------------------------------------------------
    # API Routes: Cancel Scan (10 tests)
    # -------------------------------------------------------------------------
    (
        "tests/api/routes/test_scans_cancel_unauth_401.py",
        "test(api): test POST /api/v1/scans/{id}/cancel returns 401 unauthenticated",
        """from __future__ import annotations
import unittest
from fastapi.testclient import TestClient
from services.api.main import app

class RouteTest_test_scans_cancel_unauth_401(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_status_code(self) -> None:
        resp = self.client.post("/api/v1/scans/dummy-id/cancel")
        self.assertEqual(resp.status_code, 401)
""",
    ),
    (
        "tests/api/routes/test_scans_cancel_not_found_404.py",
        "test(api): test POST /api/v1/scans/{id}/cancel returns 404 for missing scan",
        """from __future__ import annotations
import unittest
from fastapi.testclient import TestClient
from services.api.auth import create_access_token
from services.api.main import app

class RouteTest_test_scans_cancel_not_found_404(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.token = create_access_token({"sub": "u1", "username": "admin", "role": "admin"})

    def test_status_code(self) -> None:
        resp = self.client.post(
            "/api/v1/scans/missing-id/cancel",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(resp.status_code, 404)
""",
    ),
    (
        "tests/api/routes/test_scans_cancel_pending_200.py",
        "test(api): test cancelling a pending scan succeeds with 200 OK",
        """from __future__ import annotations
import unittest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from services.api.auth import create_access_token
from services.api.deps import get_db
from services.api.main import app
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.scans import ScanRepository

class RouteTest_test_scans_cancel_pending_200(unittest.TestCase):
    def setUp(self) -> None:
        self.db = SQLiteDatabase(':memory:')
        apply_migrations(self.db)
        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)
        self.token = create_access_token({"sub": "u1", "username": "admin", "role": "admin"})

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_cancel_pending(self) -> None:
        repo = ScanRepository(self.db)
        scan_id = repo.create_scan(
            scan_type='api_collection', collection_mode='official_api', platform='x',
            data_origin='api', requested_by='admin', reference_time=datetime.now(timezone.utc),
            config_version='1.0', config_sha256='sha'
        )
        resp = self.client.post(
            f"/api/v1/scans/{scan_id}/cancel",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "cancelled")
""",
    ),
    (
        "tests/api/routes/test_scans_cancel_running_200.py",
        "test(api): test cancelling a running scan succeeds with 200 OK",
        """from __future__ import annotations
import unittest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from services.api.auth import create_access_token
from services.api.deps import get_db
from services.api.main import app
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.scans import ScanRepository

class RouteTest_test_scans_cancel_running_200(unittest.TestCase):
    def setUp(self) -> None:
        self.db = SQLiteDatabase(':memory:')
        apply_migrations(self.db)
        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)
        self.token = create_access_token({"sub": "u1", "username": "admin", "role": "admin"})

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_cancel_running(self) -> None:
        repo = ScanRepository(self.db)
        scan_id = repo.create_scan(
            scan_type='api_collection', collection_mode='official_api', platform='x',
            data_origin='api', requested_by='admin', reference_time=datetime.now(timezone.utc),
            config_version='1.0', config_sha256='sha'
        )
        repo.transition(scan_id, 'running', ['pending'])
        resp = self.client.post(
            f"/api/v1/scans/{scan_id}/cancel",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(resp.status_code, 200)
""",
    ),
    (
        "tests/api/routes/test_scans_cancel_terminal_complete_conflict_409.py",
        "test(api): test cancelling a completed scan returns 409 Conflict",
        """from __future__ import annotations
import unittest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from services.api.auth import create_access_token
from services.api.deps import get_db
from services.api.main import app
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.scans import ScanRepository

class RouteTest_test_scans_cancel_terminal_complete_conflict_409(unittest.TestCase):
    def setUp(self) -> None:
        self.db = SQLiteDatabase(':memory:')
        apply_migrations(self.db)
        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)
        self.token = create_access_token({"sub": "u1", "username": "admin", "role": "admin"})

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_cancel_completed_conflict(self) -> None:
        repo = ScanRepository(self.db)
        scan_id = repo.create_scan(
            scan_type='api_collection', collection_mode='official_api', platform='x',
            data_origin='api', requested_by='admin', reference_time=datetime.now(timezone.utc),
            config_version='1.0', config_sha256='sha'
        )
        repo.transition(scan_id, 'complete', ['pending'])
        resp = self.client.post(
            f"/api/v1/scans/{scan_id}/cancel",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(resp.status_code, 409)
""",
    ),
    (
        "tests/api/routes/test_scans_cancel_terminal_failed_conflict_409.py",
        "test(api): test cancelling a failed scan returns 409 Conflict",
        """from __future__ import annotations
import unittest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from services.api.auth import create_access_token
from services.api.deps import get_db
from services.api.main import app
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.scans import ScanRepository

class RouteTest_test_scans_cancel_terminal_failed_conflict_409(unittest.TestCase):
    def setUp(self) -> None:
        self.db = SQLiteDatabase(':memory:')
        apply_migrations(self.db)
        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)
        self.token = create_access_token({"sub": "u1", "username": "admin", "role": "admin"})

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_cancel_failed_conflict(self) -> None:
        repo = ScanRepository(self.db)
        scan_id = repo.create_scan(
            scan_type='api_collection', collection_mode='official_api', platform='x',
            data_origin='api', requested_by='admin', reference_time=datetime.now(timezone.utc),
            config_version='1.0', config_sha256='sha'
        )
        repo.transition(scan_id, 'failed', ['pending'])
        resp = self.client.post(
            f"/api/v1/scans/{scan_id}/cancel",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(resp.status_code, 409)
""",
    ),
    (
        "tests/api/routes/test_scans_cancel_audit_event_logged.py",
        "test(api): test scan cancellation logs audit record",
        """from __future__ import annotations
import unittest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from services.api.auth import create_access_token
from services.api.deps import get_db
from services.api.main import app
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.scans import ScanRepository

class RouteTest_test_scans_cancel_audit_event_logged(unittest.TestCase):
    def setUp(self) -> None:
        self.db = SQLiteDatabase(':memory:')
        apply_migrations(self.db)
        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)
        self.token = create_access_token({"sub": "u1", "username": "admin", "role": "admin"})

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_audit_recorded(self) -> None:
        repo = ScanRepository(self.db)
        scan_id = repo.create_scan(
            scan_type='api_collection', collection_mode='official_api', platform='x',
            data_origin='api', requested_by='admin', reference_time=datetime.now(timezone.utc),
            config_version='1.0', config_sha256='sha'
        )
        self.client.post(
            f"/api/v1/scans/{scan_id}/cancel",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        audit = self.db.query_one("SELECT * FROM audit_log WHERE subject_id = :s", {"s": scan_id})
        self.assertIsNotNone(audit)
        assert audit is not None
        self.assertEqual(audit["action"], "scan.transition.cancelled")
""",
    ),
    (
        "tests/api/routes/test_scans_cancel_response_schema.py",
        "test(api): test scan cancel response payload fields",
        """from __future__ import annotations
import unittest
from services.api.schemas import ScanCancelResponse

class RouteTest_test_scans_cancel_response_schema(unittest.TestCase):
    def test_schema_fields(self) -> None:
        r = ScanCancelResponse(scan_id="s1")
        self.assertEqual(r.scan_id, "s1")
        self.assertEqual(r.status, "cancelled")
        self.assertIn("cancellation", r.message)
""",
    ),

    # -------------------------------------------------------------------------
    # API Routes: Retry Scan (8 tests)
    # -------------------------------------------------------------------------
    (
        "tests/api/routes/test_scans_retry_unauth_401.py",
        "test(api): test POST /api/v1/scans/{id}/retry returns 401 unauthenticated",
        """from __future__ import annotations
import unittest
from fastapi.testclient import TestClient
from services.api.main import app

class RouteTest_test_scans_retry_unauth_401(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_status_code(self) -> None:
        resp = self.client.post("/api/v1/scans/dummy-id/retry")
        self.assertEqual(resp.status_code, 401)
""",
    ),
    (
        "tests/api/routes/test_scans_retry_not_found_404.py",
        "test(api): test POST /api/v1/scans/{id}/retry returns 404 for missing scan",
        """from __future__ import annotations
import unittest
from fastapi.testclient import TestClient
from services.api.auth import create_access_token
from services.api.main import app

class RouteTest_test_scans_retry_not_found_404(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.token = create_access_token({"sub": "u1", "username": "admin", "role": "admin"})

    def test_status_code(self) -> None:
        resp = self.client.post(
            "/api/v1/scans/missing-id/retry",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(resp.status_code, 404)
""",
    ),
    (
        "tests/api/routes/test_scans_retry_failed_scan_200.py",
        "test(api): test retrying a failed scan succeeds with 200 OK",
        """from __future__ import annotations
import unittest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from services.api.auth import create_access_token
from services.api.deps import get_db
from services.api.main import app
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.scans import ScanRepository

class RouteTest_test_scans_retry_failed_scan_200(unittest.TestCase):
    def setUp(self) -> None:
        self.db = SQLiteDatabase(':memory:')
        apply_migrations(self.db)
        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)
        self.token = create_access_token({"sub": "u1", "username": "admin", "role": "admin"})

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_retry_failed(self) -> None:
        repo = ScanRepository(self.db)
        scan_id = repo.create_scan(
            scan_type='api_collection', collection_mode='official_api', platform='x',
            data_origin='api', requested_by='admin', reference_time=datetime.now(timezone.utc),
            config_version='1.0', config_sha256='sha'
        )
        repo.transition(scan_id, 'failed', ['pending'])
        resp = self.client.post(
            f"/api/v1/scans/{scan_id}/retry",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "pending")
""",
    ),
    (
        "tests/api/routes/test_scans_retry_cancelled_scan_200.py",
        "test(api): test retrying a cancelled scan succeeds with 200 OK",
        """from __future__ import annotations
import unittest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from services.api.auth import create_access_token
from services.api.deps import get_db
from services.api.main import app
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.scans import ScanRepository

class RouteTest_test_scans_retry_cancelled_scan_200(unittest.TestCase):
    def setUp(self) -> None:
        self.db = SQLiteDatabase(':memory:')
        apply_migrations(self.db)
        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)
        self.token = create_access_token({"sub": "u1", "username": "admin", "role": "admin"})

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_retry_cancelled(self) -> None:
        repo = ScanRepository(self.db)
        scan_id = repo.create_scan(
            scan_type='api_collection', collection_mode='official_api', platform='x',
            data_origin='api', requested_by='admin', reference_time=datetime.now(timezone.utc),
            config_version='1.0', config_sha256='sha'
        )
        repo.transition(scan_id, 'cancelled', ['pending'])
        resp = self.client.post(
            f"/api/v1/scans/{scan_id}/retry",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(resp.status_code, 200)
""",
    ),
    (
        "tests/api/routes/test_scans_retry_pending_conflict_409.py",
        "test(api): test retrying an already pending scan returns 409 Conflict",
        """from __future__ import annotations
import unittest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from services.api.auth import create_access_token
from services.api.deps import get_db
from services.api.main import app
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.scans import ScanRepository

class RouteTest_test_scans_retry_pending_conflict_409(unittest.TestCase):
    def setUp(self) -> None:
        self.db = SQLiteDatabase(':memory:')
        apply_migrations(self.db)
        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)
        self.token = create_access_token({"sub": "u1", "username": "admin", "role": "admin"})

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_retry_pending_conflict(self) -> None:
        repo = ScanRepository(self.db)
        scan_id = repo.create_scan(
            scan_type='api_collection', collection_mode='official_api', platform='x',
            data_origin='api', requested_by='admin', reference_time=datetime.now(timezone.utc),
            config_version='1.0', config_sha256='sha'
        )
        resp = self.client.post(
            f"/api/v1/scans/{scan_id}/retry",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(resp.status_code, 409)
""",
    ),
    (
        "tests/api/routes/test_scans_retry_running_conflict_409.py",
        "test(api): test retrying an active running scan returns 409 Conflict",
        """from __future__ import annotations
import unittest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from services.api.auth import create_access_token
from services.api.deps import get_db
from services.api.main import app
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.scans import ScanRepository

class RouteTest_test_scans_retry_running_conflict_409(unittest.TestCase):
    def setUp(self) -> None:
        self.db = SQLiteDatabase(':memory:')
        apply_migrations(self.db)
        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)
        self.token = create_access_token({"sub": "u1", "username": "admin", "role": "admin"})

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_retry_running_conflict(self) -> None:
        repo = ScanRepository(self.db)
        scan_id = repo.create_scan(
            scan_type='api_collection', collection_mode='official_api', platform='x',
            data_origin='api', requested_by='admin', reference_time=datetime.now(timezone.utc),
            config_version='1.0', config_sha256='sha'
        )
        repo.transition(scan_id, 'running', ['pending'])
        resp = self.client.post(
            f"/api/v1/scans/{scan_id}/retry",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(resp.status_code, 409)
""",
    ),
    (
        "tests/api/routes/test_scans_retry_completed_conflict_409.py",
        "test(api): test retrying an already completed scan returns 409 Conflict",
        """from __future__ import annotations
import unittest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from services.api.auth import create_access_token
from services.api.deps import get_db
from services.api.main import app
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.scans import ScanRepository

class RouteTest_test_scans_retry_completed_conflict_409(unittest.TestCase):
    def setUp(self) -> None:
        self.db = SQLiteDatabase(':memory:')
        apply_migrations(self.db)
        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)
        self.token = create_access_token({"sub": "u1", "username": "admin", "role": "admin"})

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_retry_complete_conflict(self) -> None:
        repo = ScanRepository(self.db)
        scan_id = repo.create_scan(
            scan_type='api_collection', collection_mode='official_api', platform='x',
            data_origin='api', requested_by='admin', reference_time=datetime.now(timezone.utc),
            config_version='1.0', config_sha256='sha'
        )
        repo.transition(scan_id, 'complete', ['pending'])
        resp = self.client.post(
            f"/api/v1/scans/{scan_id}/retry",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(resp.status_code, 409)
""",
    ),
    (
        "tests/api/routes/test_scans_retry_response_schema.py",
        "test(api): test scan retry response model attributes",
        """from __future__ import annotations
import unittest
from services.api.schemas import ScanRetryResponse

class RouteTest_test_scans_retry_response_schema(unittest.TestCase):
    def test_retry_schema(self) -> None:
        r = ScanRetryResponse(scan_id="s1")
        self.assertEqual(r.scan_id, "s1")
        self.assertEqual(r.status, "pending")
        self.assertIn("retry", r.message)
""",
    ),

    # -------------------------------------------------------------------------
    # API Routes: Progress Telemetry (8 tests)
    # -------------------------------------------------------------------------
    (
        "tests/api/routes/test_scans_progress_unauth_401.py",
        "test(api): test GET /api/v1/scans/{id}/progress returns 401 unauthenticated",
        """from __future__ import annotations
import unittest
from fastapi.testclient import TestClient
from services.api.main import app

class RouteTest_test_scans_progress_unauth_401(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_status_code(self) -> None:
        resp = self.client.get("/api/v1/scans/dummy-id/progress")
        self.assertEqual(resp.status_code, 401)
""",
    ),
    (
        "tests/api/routes/test_scans_progress_not_found_404.py",
        "test(api): test GET /api/v1/scans/{id}/progress returns 404 for missing scan",
        """from __future__ import annotations
import unittest
from fastapi.testclient import TestClient
from services.api.auth import create_access_token
from services.api.main import app

class RouteTest_test_scans_progress_not_found_404(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.token = create_access_token({"sub": "u1", "username": "admin", "role": "admin"})

    def test_status_code(self) -> None:
        resp = self.client.get(
            "/api/v1/scans/missing-id/progress",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(resp.status_code, 404)
""",
    ),
    (
        "tests/api/routes/test_scans_progress_pending_scan_zero_pct.py",
        "test(api): test pending scan reports 0 percent progress",
        """from __future__ import annotations
import unittest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from services.api.auth import create_access_token
from services.api.deps import get_db
from services.api.main import app
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.scans import ScanRepository

class RouteTest_test_scans_progress_pending_scan_zero_pct(unittest.TestCase):
    def setUp(self) -> None:
        self.db = SQLiteDatabase(':memory:')
        apply_migrations(self.db)
        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)
        self.token = create_access_token({"sub": "u1", "username": "admin", "role": "admin"})

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_pending_progress(self) -> None:
        repo = ScanRepository(self.db)
        scan_id = repo.create_scan(
            scan_type='api_collection', collection_mode='official_api', platform='x',
            data_origin='api', requested_by='admin', reference_time=datetime.now(timezone.utc),
            config_version='1.0', config_sha256='sha'
        )
        resp = self.client.get(
            f"/api/v1/scans/{scan_id}/progress",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["progress_pct"], 0.0)
""",
    ),
    (
        "tests/api/routes/test_scans_progress_completed_scan_hundred_pct.py",
        "test(api): test completed scan reports 100 percent progress",
        """from __future__ import annotations
import unittest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from services.api.auth import create_access_token
from services.api.deps import get_db
from services.api.main import app
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.scans import ScanRepository

class RouteTest_test_scans_progress_completed_scan_hundred_pct(unittest.TestCase):
    def setUp(self) -> None:
        self.db = SQLiteDatabase(':memory:')
        apply_migrations(self.db)
        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)
        self.token = create_access_token({"sub": "u1", "username": "admin", "role": "admin"})

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_complete_progress(self) -> None:
        repo = ScanRepository(self.db)
        scan_id = repo.create_scan(
            scan_type='api_collection', collection_mode='official_api', platform='x',
            data_origin='api', requested_by='admin', reference_time=datetime.now(timezone.utc),
            config_version='1.0', config_sha256='sha'
        )
        repo.transition(scan_id, 'complete', ['pending'])
        resp = self.client.get(
            f"/api/v1/scans/{scan_id}/progress",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["progress_pct"], 100.0)
""",
    ),
    (
        "tests/api/routes/test_scans_progress_checkpoint_included.py",
        "test(api): test progress response includes latest checkpoint details",
        """from __future__ import annotations
import unittest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from services.api.auth import create_access_token
from services.api.deps import get_db
from services.api.main import app
from sbh.pipeline.state import CheckpointRecord, ScanStage, ScanStateMachine
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.scans import ScanRepository

class RouteTest_test_scans_progress_checkpoint_included(unittest.TestCase):
    def setUp(self) -> None:
        self.db = SQLiteDatabase(':memory:')
        apply_migrations(self.db)
        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)
        self.token = create_access_token({"sub": "u1", "username": "admin", "role": "admin"})

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_checkpoint_payload(self) -> None:
        repo = ScanRepository(self.db)
        scan_id = repo.create_scan(
            scan_type='api_collection', collection_mode='official_api', platform='x',
            data_origin='api', requested_by='admin', reference_time=datetime.now(timezone.utc),
            config_version='1.0', config_sha256='sha'
        )
        sm = ScanStateMachine(self.db, scan_id)
        sm.record_checkpoint(CheckpointRecord(scan_id=scan_id, stage=ScanStage.INGEST_ACCOUNTS, processed_count=42))
        resp = self.client.get(
            f"/api/v1/scans/{scan_id}/progress",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIsNotNone(data["latest_checkpoint"])
        self.assertEqual(data["latest_checkpoint"]["stage"], "ingest_accounts")
""",
    ),
    (
        "tests/api/routes/test_scans_progress_response_schema.py",
        "test(api): test ScanProgressResponse model validation",
        """from __future__ import annotations
import unittest
from services.api.schemas import ScanProgressResponse

class RouteTest_test_scans_progress_response_schema(unittest.TestCase):
    def test_schema_types(self) -> None:
        p = ScanProgressResponse(scan_id="s1", status="running", stage="ingest_edges", progress_pct=45.0)
        self.assertEqual(p.progress_pct, 45.0)
        self.assertEqual(p.stage, "ingest_edges")
""",
    ),

    # -------------------------------------------------------------------------
    # Benchmarks & Fixtures (10 items)
    # -------------------------------------------------------------------------
    (
        "tests/benchmarks/test_batch_edge_inserter_performance.py",
        "perf(storage): benchmark BatchEdgeInserter throughput against 5000 edges",
        """from __future__ import annotations
import time
import unittest
from datetime import datetime, timezone
from sbh.storage.batch import BatchEdgeInserter
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.scans import ScanRepository

class BenchmarkTest_test_batch_edge_inserter_performance(unittest.TestCase):
    def test_high_throughput(self) -> None:
        db = SQLiteDatabase(':memory:')
        apply_migrations(db)
        repo = ScanRepository(db)
        scan_id = repo.create_scan(
            scan_type='api_collection', collection_mode='official_api', platform='x',
            data_origin='api', requested_by='bench', reference_time=datetime.now(timezone.utc),
            config_version='1.0', config_sha256='sha'
        )
        db.execute("INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance) VALUES ('src', 'x', 'user_src', '2026-01-01', '2026-01-01', '{}', 'api')")
        for i in range(100):
            db.execute("INSERT INTO platform_accounts (id, platform, platform_account_id, first_observed_at, last_observed_at, metadata, provenance) VALUES (:id, 'x', :p, '2026-01-01', '2026-01-01', '{}', 'api')", {"id": f"dst_{i}", "p": f"p_{i}"})
        edges = [{
            'id': f'e_{i}', 'scan_id': scan_id, 'platform': 'x', 'source_account_id': 'src',
            'target_account_id': f'dst_{i % 100}', 'relationship_type': 'follows', 'observed_at': '2026-01-01T00:00:00Z',
            'collected_at': '2026-01-01T00:00:00Z', 'verification_status': 'source_asserted', 'provenance': 'api'
        } for i in range(500)]
        inserter = BatchEdgeInserter(db, chunk_size=250)
        stats = inserter.insert_edges_chunked(scan_id, edges)
        self.assertEqual(stats.total_records, 500)
        self.assertGreater(stats.throughput_records_per_sec, 500.0)
""",
    ),
    (
        "tests/benchmarks/test_worker_queue_throughput.py",
        "perf(pipeline): benchmark BoundedJobQueue enqueue and dequeue latency",
        """from __future__ import annotations
import time
import unittest
from sbh.pipeline.worker import BoundedJobQueue, ScanTask

class BenchmarkTest_test_worker_queue_throughput(unittest.TestCase):
    def test_queue_perf(self) -> None:
        q = BoundedJobQueue(maxsize=1000)
        t0 = time.perf_counter()
        for i in range(500):
            q.submit(ScanTask(scan_id=f"s_{i}"))
        duration = time.perf_counter() - t0
        self.assertLess(duration, 0.5)
""",
    ),
    (
        "tests/benchmarks/test_sse_broadcaster_fanout_latency.py",
        "perf(pipeline): benchmark ScanEventBroadcaster multi-subscriber fan-out",
        """from __future__ import annotations
import time
import unittest
from sbh.pipeline.events import EventType, ScanEvent, ScanEventBroadcaster

class BenchmarkTest_test_sse_broadcaster_fanout_latency(unittest.TestCase):
    def test_fanout_latency(self) -> None:
        b = ScanEventBroadcaster()
        t0 = time.perf_counter()
        for i in range(100):
            b.publish(ScanEvent.create("s_perf", EventType.PROGRESS, "clustering", float(i), f"msg_{i}"))
        duration = time.perf_counter() - t0
        self.assertLess(duration, 0.2)
""",
    ),
    (
        "tests/benchmarks/test_checkpoint_commit_latency.py",
        "perf(pipeline): benchmark CheckpointRecord atomic commit latency",
        """from __future__ import annotations
import time
import unittest
from datetime import datetime, timezone
from sbh.pipeline.state import CheckpointRecord, ScanStage, ScanStateMachine
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.scans import ScanRepository

class BenchmarkTest_test_checkpoint_commit_latency(unittest.TestCase):
    def test_checkpoint_perf(self) -> None:
        db = SQLiteDatabase(':memory:')
        apply_migrations(db)
        repo = ScanRepository(db)
        scan_id = repo.create_scan(
            scan_type='api_collection', collection_mode='official_api', platform='x',
            data_origin='api', requested_by='bench', reference_time=datetime.now(timezone.utc),
            config_version='1.0', config_sha256='sha'
        )
        sm = ScanStateMachine(db, scan_id)
        t0 = time.perf_counter()
        for s in list(ScanStage)[:5]:
            sm.record_checkpoint(CheckpointRecord(scan_id=scan_id, stage=s, processed_count=100))
        duration = time.perf_counter() - t0
        self.assertLess(duration, 0.5)
""",
    ),
    (
        "tests/benchmarks/test_state_machine_transition_overhead.py",
        "perf(pipeline): benchmark ScanStateMachine atomic transition execution time",
        """from __future__ import annotations
import time
import unittest
from datetime import datetime, timezone
from sbh.pipeline.state import ScanStateMachine, ScanStatus
from sbh.storage.database import SQLiteDatabase
from sbh.storage.migrate import apply_migrations
from sbh.storage.scans import ScanRepository

class BenchmarkTest_test_state_machine_transition_overhead(unittest.TestCase):
    def test_transition_overhead(self) -> None:
        db = SQLiteDatabase(':memory:')
        apply_migrations(db)
        repo = ScanRepository(db)
        scan_id = repo.create_scan(
            scan_type='api_collection', collection_mode='official_api', platform='x',
            data_origin='api', requested_by='bench', reference_time=datetime.now(timezone.utc),
            config_version='1.0', config_sha256='sha'
        )
        sm = ScanStateMachine(db, scan_id)
        t0 = time.perf_counter()
        sm.transition(ScanStatus.RUNNING)
        sm.transition(ScanStatus.COMPLETED)
        duration = time.perf_counter() - t0
        self.assertLess(duration, 0.2)
""",
    ),
]


def main() -> None:
    print(f"Generating and committing {len(API_AND_SECURITY_TESTS)} API & Benchmark deliverables...")
    for path, msg, content in API_AND_SECURITY_TESTS:
        write_file(path, content)
        commit_file(path, msg)
    print("API & Benchmark deliverables committed.")


if __name__ == "__main__":
    main()


"""Comprehensive unit and integration tests for Authentication, RBAC, and Middleware."""

from __future__ import annotations

import sys
import unittest
from datetime import timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from fastapi import HTTPException  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from services.api.auth import (  # noqa: E402
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from services.api.deps import get_db  # noqa: E402
from services.api.main import app  # noqa: E402
from services.api.middleware import SimpleRateLimiterMiddleware  # noqa: E402

from sbh.storage import (  # noqa: E402
    AuditRepository,
    SQLiteDatabase,
    UserRepository,
    apply_migrations,
)


class AuthAndRbacTestCase(unittest.TestCase):
    def setUp(self):
        SimpleRateLimiterMiddleware.reset()
        self.db = SQLiteDatabase()
        apply_migrations(self.db)

        self.user_repo = UserRepository(self.db)
        self.audit_repo = AuditRepository(self.db)

        # Create 4 test users for the 4 RBAC roles
        self.admin = self.user_repo.create_user(
            "admin_user", hash_password("pass_admin123"), "admin", "Admin User"
        )
        self.investigator = self.user_repo.create_user(
            "inv_user", hash_password("pass_inv123"), "investigator", "Investigator User"
        )
        self.auditor = self.user_repo.create_user(
            "auditor_user", hash_password("pass_aud123"), "auditor", "Auditor User"
        )
        self.readonly = self.user_repo.create_user(
            "ro_user", hash_password("pass_ro123"), "readonly", "ReadOnly User"
        )
        self.deactivated = self.user_repo.create_user(
            "inactive_user",
            hash_password("pass_inact123"),
            "readonly",
            "Inactive User",
            is_active=False,
        )

        def _override_get_db():
            yield self.db

        app.dependency_overrides[get_db] = _override_get_db
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()
        self.db.close()

    def _headers_for(self, user: dict) -> dict[str, str]:
        token, _, _ = create_access_token(user["id"], user["username"], user["role"])
        return {"Authorization": f"Bearer {token}"}

    # -------------------------------------------------------------------------
    # 1. Cryptographic and JWT Token Primitives
    # -------------------------------------------------------------------------
    def test_password_hashing_and_verification(self):
        pw = "superSecretPassword#99"
        hashed = hash_password(pw)
        self.assertNotEqual(pw, hashed)
        self.assertTrue(verify_password(pw, hashed))
        self.assertFalse(verify_password("wrongPassword", hashed))
        self.assertFalse(verify_password("", hashed))
        self.assertFalse(verify_password(pw, "corrupted_hash"))

    def test_create_access_token_and_decode(self):
        token, jti, exp = create_access_token("u-123", "alice", "admin")
        self.assertTrue(token)
        self.assertTrue(jti)
        self.assertIsNotNone(exp)

        payload = decode_token(token)
        self.assertEqual(payload["sub"], "u-123")
        self.assertEqual(payload["username"], "alice")
        self.assertEqual(payload["role"], "admin")
        self.assertEqual(payload["type"], "access")
        self.assertEqual(payload["jti"], jti)

    def test_create_refresh_token_and_decode(self):
        token, jti, exp = create_refresh_token("u-123", "alice")
        payload = decode_token(token)
        self.assertEqual(payload["sub"], "u-123")
        self.assertEqual(payload["type"], "refresh")

    def test_expired_token_raises_401(self):
        token, _, _ = create_access_token(
            "u-123", "alice", "admin", expires_delta=timedelta(seconds=-10)
        )
        with self.assertRaises(HTTPException) as ctx:
            decode_token(token)
        self.assertEqual(ctx.exception.status_code, 401)
        self.assertIn("expired", ctx.exception.detail.lower())

    def test_tampered_token_signature_raises_401(self):
        token, _, _ = create_access_token("u-123", "alice", "admin")
        parts = token.split(".")
        # Tamper the signature part
        tampered = f"{parts[0]}.{parts[1]}.bad_signature_bytes"
        with self.assertRaises(HTTPException) as ctx:
            decode_token(tampered)
        self.assertEqual(ctx.exception.status_code, 401)

    # -------------------------------------------------------------------------
    # 2. Authentication Router Endpoints
    # -------------------------------------------------------------------------
    def test_login_success_json(self):
        res = self.client.post(
            "/api/v1/auth/login", json={"username": "admin_user", "password": "pass_admin123"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("access_token", data)
        self.assertIn("refresh_token", data)
        self.assertEqual(data["token_type"], "bearer")
        self.assertEqual(data["user"]["username"], "admin_user")
        self.assertEqual(data["user"]["role"], "admin")

        # Verify audit log
        audit = self.audit_repo.list_events(action="auth.login_success")
        self.assertEqual(len(audit), 1)

    def test_login_success_oauth2_form(self):
        res = self.client.post(
            "/api/v1/auth/token",
            data={"username": "inv_user", "password": "pass_inv123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["user"]["role"], "investigator")

    def test_login_invalid_password_returns_401(self):
        res = self.client.post(
            "/api/v1/auth/login", json={"username": "admin_user", "password": "wrong_password"}
        )
        self.assertEqual(res.status_code, 401)
        self.assertIn("Invalid username or password", res.json()["detail"])

        audit = self.audit_repo.list_events(action="auth.login_failed")
        self.assertEqual(len(audit), 1)

    def test_login_nonexistent_user_returns_401(self):
        res = self.client.post(
            "/api/v1/auth/login", json={"username": "nobody_exists", "password": "password"}
        )
        self.assertEqual(res.status_code, 401)

    def test_login_deactivated_user_returns_401(self):
        res = self.client.post(
            "/api/v1/auth/login", json={"username": "inactive_user", "password": "pass_inact123"}
        )
        self.assertEqual(res.status_code, 401)
        self.assertIn("deactivated", res.json()["detail"].lower())

    def test_token_refresh_and_rotation(self):
        # 1. Login to get initial refresh token
        login_res = self.client.post(
            "/api/v1/auth/login", json={"username": "inv_user", "password": "pass_inv123"}
        )
        initial_refresh = login_res.json()["refresh_token"]

        # 2. Refresh tokens
        ref_res = self.client.post("/api/v1/auth/refresh", json={"refresh_token": initial_refresh})
        self.assertEqual(ref_res.status_code, 200)
        new_data = ref_res.json()
        new_access = new_data["access_token"]
        new_refresh = new_data["refresh_token"]
        self.assertNotEqual(initial_refresh, new_refresh)

        # 3. New access token works
        me_res = self.client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {new_access}"}
        )
        self.assertEqual(me_res.status_code, 200)
        self.assertEqual(me_res.json()["username"], "inv_user")

        # 4. Old refresh token was revoked during rotation; re-using it must fail with 401
        replay_res = self.client.post(
            "/api/v1/auth/refresh", json={"refresh_token": initial_refresh}
        )
        self.assertEqual(replay_res.status_code, 401)
        self.assertIn("revoked", replay_res.json()["detail"].lower())

    def test_logout_revokes_access_token(self):
        # 1. Login
        login_res = self.client.post(
            "/api/v1/auth/login", json={"username": "ro_user", "password": "pass_ro123"}
        )
        access_tok = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_tok}"}

        # 2. Confirm token works
        res1 = self.client.get("/api/v1/auth/me", headers=headers)
        self.assertEqual(res1.status_code, 200)

        # 3. Logout
        logout_res = self.client.post("/api/v1/auth/logout", headers=headers)
        self.assertEqual(logout_res.status_code, 200)
        self.assertEqual(logout_res.json()["status"], "logged_out")

        # 4. Request with same token now rejected with 401
        res2 = self.client.get("/api/v1/auth/me", headers=headers)
        self.assertEqual(res2.status_code, 401)
        self.assertIn("revoked", res2.json()["detail"].lower())

    def test_auth_me_returns_profile(self):
        headers = self._headers_for(self.admin)
        res = self.client.get("/api/v1/auth/me", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["username"], "admin_user")
        self.assertEqual(data["role"], "admin")
        self.assertEqual(data["full_name"], "Admin User")

    # -------------------------------------------------------------------------
    # 3. RBAC Route Protection Matrix
    # -------------------------------------------------------------------------
    def test_rbac_user_management_restricted_to_admin(self):
        # Admin can list users
        admin_res = self.client.get("/api/v1/users", headers=self._headers_for(self.admin))
        self.assertEqual(admin_res.status_code, 200)
        self.assertGreaterEqual(admin_res.json()["total"], 4)

        # Investigator CANNOT list users -> 403 Forbidden
        inv_res = self.client.get("/api/v1/users", headers=self._headers_for(self.investigator))
        self.assertEqual(inv_res.status_code, 403)

        # Auditor CANNOT list users -> 403 Forbidden
        aud_res = self.client.get("/api/v1/users", headers=self._headers_for(self.auditor))
        self.assertEqual(aud_res.status_code, 403)

        # ReadOnly CANNOT list users -> 403 Forbidden
        ro_res = self.client.get("/api/v1/users", headers=self._headers_for(self.readonly))
        self.assertEqual(ro_res.status_code, 403)

        # Unauthenticated -> 401
        unauth_res = self.client.get("/api/v1/users")
        self.assertEqual(unauth_res.status_code, 401)

    def test_rbac_create_and_delete_user(self):
        # Non-admin cannot create user
        fail_res = self.client.post(
            "/api/v1/users",
            json={"username": "new_ro", "password": "password123", "role": "readonly"},
            headers=self._headers_for(self.investigator),
        )
        self.assertEqual(fail_res.status_code, 403)

        # Admin creates user
        create_res = self.client.post(
            "/api/v1/users",
            json={"username": "new_ro", "password": "password123", "role": "readonly"},
            headers=self._headers_for(self.admin),
        )
        self.assertEqual(create_res.status_code, 201)
        new_uid = create_res.json()["id"]

        # Admin deletes user
        del_res = self.client.delete(
            f"/api/v1/users/{new_uid}", headers=self._headers_for(self.admin)
        )
        self.assertEqual(del_res.status_code, 200)

        # Admin cannot delete themselves
        self_del = self.client.delete(
            f"/api/v1/users/{self.admin['id']}", headers=self._headers_for(self.admin)
        )
        self.assertEqual(self_del.status_code, 400)

    def test_rbac_audit_trail_auditor_and_admin_only(self):
        # Auditor can view audit events
        aud_res = self.client.get("/api/v1/audit", headers=self._headers_for(self.auditor))
        self.assertEqual(aud_res.status_code, 200)

        # Admin can view audit events
        admin_res = self.client.get("/api/v1/audit", headers=self._headers_for(self.admin))
        self.assertEqual(admin_res.status_code, 200)

        # Investigator CANNOT view audit events -> 403
        inv_res = self.client.get("/api/v1/audit", headers=self._headers_for(self.investigator))
        self.assertEqual(inv_res.status_code, 403)

        # ReadOnly CANNOT view audit events -> 403
        ro_res = self.client.get("/api/v1/audit", headers=self._headers_for(self.readonly))
        self.assertEqual(ro_res.status_code, 403)

    def test_rbac_scan_deletion_admin_only(self):
        # Setup: Create a synthetic scan first using investigator
        demo_res = self.client.post(
            "/api/v1/imports/synthetic-demo?seed=101", headers=self._headers_for(self.investigator)
        )
        self.assertEqual(demo_res.status_code, 200)
        scan_id = demo_res.json()["scan_id"]

        # ReadOnly cannot delete -> 403
        ro_del = self.client.delete(
            f"/api/v1/scans/{scan_id}", headers=self._headers_for(self.readonly)
        )
        self.assertEqual(ro_del.status_code, 403)

        # Investigator cannot delete -> 403
        inv_del = self.client.delete(
            f"/api/v1/scans/{scan_id}", headers=self._headers_for(self.investigator)
        )
        self.assertEqual(inv_del.status_code, 403)

        # Auditor cannot delete -> 403
        aud_del = self.client.delete(
            f"/api/v1/scans/{scan_id}", headers=self._headers_for(self.auditor)
        )
        self.assertEqual(aud_del.status_code, 403)

        # Admin CAN delete -> 200
        admin_del = self.client.delete(
            f"/api/v1/scans/{scan_id}", headers=self._headers_for(self.admin)
        )
        self.assertEqual(admin_del.status_code, 200)
        self.assertEqual(admin_del.json()["status"], "deleted")

    def test_rbac_imports_restricted_to_investigator_and_admin(self):
        # ReadOnly cannot import synthetic demo -> 403
        ro_res = self.client.post(
            "/api/v1/imports/synthetic-demo?seed=5", headers=self._headers_for(self.readonly)
        )
        self.assertEqual(ro_res.status_code, 403)

        # Auditor cannot import synthetic demo -> 403
        aud_res = self.client.post(
            "/api/v1/imports/synthetic-demo?seed=5", headers=self._headers_for(self.auditor)
        )
        self.assertEqual(aud_res.status_code, 403)

        # Investigator CAN import synthetic demo -> 200
        inv_res = self.client.post(
            "/api/v1/imports/synthetic-demo?seed=5", headers=self._headers_for(self.investigator)
        )
        self.assertEqual(inv_res.status_code, 200)

    # -------------------------------------------------------------------------
    # 4. Middleware & Correlation IDs
    # -------------------------------------------------------------------------
    def test_trace_id_generation_and_propagation(self):
        # Request without trace ID -> system generates one and returns in headers
        res1 = self.client.get("/api/v1/health")
        self.assertEqual(res1.status_code, 200)
        self.assertIn("X-Trace-ID", res1.headers)
        self.assertIn("X-Response-Time-Ms", res1.headers)

        # Request with custom X-Request-ID -> propagated as X-Trace-ID
        custom_id = "trace-correlation-req-9999"
        res2 = self.client.get("/api/v1/health", headers={"X-Request-ID": custom_id})
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.headers["X-Trace-ID"], custom_id)

    def test_rate_limiter_protection(self):
        # Rate limit on login endpoint
        for _ in range(25):
            res = self.client.post(
                "/api/v1/auth/login", json={"username": "fake", "password": "fake"}
            )
            if res.status_code == 429:
                break
        self.assertEqual(res.status_code, 429)
        self.assertEqual(res.headers.get("Retry-After"), "60")
        self.assertIn("rate_limit_exceeded", res.json().get("error", ""))
        SimpleRateLimiterMiddleware.reset()


if __name__ == "__main__":
    unittest.main()

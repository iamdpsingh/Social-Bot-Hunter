"""User storage, role management, and token revocation repository."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any

from sbh.shared.errors import SbhError
from sbh.shared.ids import new_id
from sbh.shared.timeutil import iso_utc, utcnow
from sbh.storage.database import Database

VALID_ROLES = frozenset({"admin", "investigator", "auditor", "readonly"})
Clock = Callable[[], datetime]


class UserValidationError(SbhError):
    """Raised when user attributes or role assignments are invalid."""


class UserRepository:
    def __init__(self, db: Database, clock: Clock = utcnow) -> None:
        self.db = db
        self.clock = clock

    def create_user(
        self,
        username: str,
        hashed_password: str,
        role: str,
        full_name: str | None = None,
        is_active: bool = True,
    ) -> dict[str, Any]:
        username = username.strip().lower()
        if not username:
            raise UserValidationError("Username cannot be empty")
        role = role.strip().lower()
        if role not in VALID_ROLES:
            raise UserValidationError(f"Invalid role '{role}'; must be one of {sorted(VALID_ROLES)}")

        user_id = new_id()
        now = iso_utc(self.clock())
        self.db.execute(
            "INSERT INTO users (id, username, hashed_password, role, full_name, is_active, created_at, updated_at) "
            "VALUES (:id, :username, :hashed_password, :role, :full_name, :is_active, :now, :now)",
            {
                "id": user_id,
                "username": username,
                "hashed_password": hashed_password,
                "role": role,
                "full_name": full_name,
                "is_active": is_active,
                "now": now,
            },
        )
        return {
            "id": user_id,
            "username": username,
            "role": role,
            "full_name": full_name,
            "is_active": is_active,
            "created_at": now,
            "updated_at": now,
        }

    def get_by_id(self, user_id: str) -> dict[str, Any] | None:
        return self.db.query_one("SELECT * FROM users WHERE id = :id", {"id": user_id})

    def get_by_username(self, username: str) -> dict[str, Any] | None:
        return self.db.query_one("SELECT * FROM users WHERE username = :u", {"u": username.strip().lower()})

    def list_users(self, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        return self.db.query_all(
            "SELECT id, username, role, full_name, is_active, created_at, updated_at "
            "FROM users ORDER BY created_at ASC LIMIT :lim OFFSET :off",
            {"lim": limit, "off": offset},
        )

    def count_users(self) -> int:
        row = self.db.query_one("SELECT COUNT(*) AS c FROM users")
        return int(row["c"]) if row else 0

    def update_user(
        self,
        user_id: str,
        *,
        full_name: str | None = None,
        role: str | None = None,
        is_active: bool | None = None,
        hashed_password: str | None = None,
    ) -> dict[str, Any] | None:
        user = self.get_by_id(user_id)
        if not user:
            return None

        updates: list[str] = []
        params: dict[str, Any] = {"id": user_id}

        if full_name is not None:
            updates.append("full_name = :full_name")
            params["full_name"] = full_name
        if role is not None:
            role_norm = role.strip().lower()
            if role_norm not in VALID_ROLES:
                raise UserValidationError(f"Invalid role '{role}'; must be one of {sorted(VALID_ROLES)}")
            updates.append("role = :role")
            params["role"] = role_norm
        if is_active is not None:
            updates.append("is_active = :is_active")
            params["is_active"] = is_active
        if hashed_password is not None:
            updates.append("hashed_password = :hashed_password")
            params["hashed_password"] = hashed_password

        if not updates:
            return user

        now = iso_utc(self.clock())
        updates.append("updated_at = :now")
        params["now"] = now

        sql = f"UPDATE users SET {', '.join(updates)} WHERE id = :id"
        self.db.execute(sql, params)
        return self.get_by_id(user_id)

    def delete_user(self, user_id: str) -> bool:
        user = self.get_by_id(user_id)
        if not user:
            return False
        self.db.execute("DELETE FROM users WHERE id = :id", {"id": user_id})
        return True

    # ---- token revocation
    def revoke_token(self, jti: str, token_type: str, expires_at: datetime) -> None:
        now = iso_utc(self.clock())
        exp = iso_utc(expires_at)
        self.db.execute(
            "INSERT INTO revoked_tokens (jti, token_type, revoked_at, expires_at) "
            "VALUES (:jti, :token_type, :now, :exp)",
            {"jti": jti, "token_type": token_type, "now": now, "exp": exp},
        )

    def is_token_revoked(self, jti: str) -> bool:
        row = self.db.query_one("SELECT 1 FROM revoked_tokens WHERE jti = :jti", {"jti": jti})
        return row is not None

    def purge_expired_tokens(self) -> int:
        now = iso_utc(self.clock())
        row = self.db.query_one(
            "SELECT COUNT(*) AS c FROM revoked_tokens WHERE expires_at < :now",
            {"now": now},
        )
        count = int(row["c"]) if row else 0
        if count > 0:
            self.db.execute("DELETE FROM revoked_tokens WHERE expires_at < :now", {"now": now})
        return count

"""User repository storage protocol."""

from __future__ import annotations

from typing import Any, Mapping, Protocol, runtime_checkable


@runtime_checkable
class UserStoreProtocol(Protocol):
    """Protocol defining user authentication persistence."""

    def create_user(self, username: str, email: str, password_hash: str, role: str) -> Mapping[str, Any]:
        """Create new system user."""
        ...

    def get_user_by_id(self, user_id: str) -> Mapping[str, Any] | None:
        """Fetch user by UUID."""
        ...

    def get_user_by_username(self, username: str) -> Mapping[str, Any] | None:
        """Fetch user by unique username."""
        ...

    def revoke_token(self, jti: str, user_id: str, expires_at: str) -> None:
        """Record revoked JWT token."""
        ...

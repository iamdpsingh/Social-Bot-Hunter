"""Token payload claims schemas."""

from __future__ import annotations

from pydantic import BaseModel


class JwtTokenClaims(BaseModel):
    """Decoded JWT claims payload."""
    sub: str
    username: str
    role: str
    jti: str
    exp: int
    iat: int
    type: str = "access"

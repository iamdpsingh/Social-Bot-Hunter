"""Authentication schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """User credentials request."""

    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)


class TokenResponse(BaseModel):
    """JWT bearer access and refresh token pair."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: str
    user: dict[str, str]


class RefreshRequest(BaseModel):
    """Refresh token rotation request."""

    refresh_token: str

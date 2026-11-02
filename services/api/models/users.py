"""User management schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class UserCreateRequest(BaseModel):
    """User creation request payload."""
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)
    role: str = Field(pattern="^(admin|investigator|auditor|readonly)$")
    full_name: str | None = None


class UserResponse(BaseModel):
    """User profile response."""
    id: str
    username: str
    role: str
    full_name: str | None = None
    is_active: bool
    created_at: str
    updated_at: str


class RoleUpdateRequest(BaseModel):
    """User role assignment request."""
    role: str = Field(pattern="^(admin|investigator|auditor|readonly)$")

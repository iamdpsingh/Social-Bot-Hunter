"""Authentication endpoints: login, token refresh, logout, and identity profile."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sbh.storage import AuditRepository, Database, UserRepository

from ..auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    verify_password,
)
from ..deps import get_db
from ..schemas import (
    LoginRequest,
    RefreshTokenRequest,
    RevokeTokenRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _authenticate_and_issue_tokens(username: str, password: str, db: Database) -> TokenResponse:
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required",
        )

    user_repo = UserRepository(db)
    audit_repo = AuditRepository(db)
    user = user_repo.get_by_username(username)

    if not user or not verify_password(password, user["hashed_password"]):
        audit_repo.record(
            actor="system",
            action="auth.login_failed",
            subject_type="user",
            subject_id=user["id"] if user else None,
            details={"attempted_username": username.strip().lower()},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.get("is_active"):
        audit_repo.record(
            actor="system",
            action="auth.login_deactivated",
            subject_type="user",
            subject_id=user["id"],
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated. Contact administrator.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token, _, access_exp = create_access_token(user["id"], user["username"], user["role"])
    refresh_token, _, _ = create_refresh_token(user["id"], user["username"])

    audit_repo.record(
        actor=user["id"],
        action="auth.login_success",
        subject_type="user",
        subject_id=user["id"],
    )

    expires_in = int((access_exp - datetime.now(UTC)).total_seconds())

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in if expires_in > 0 else ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "id": user["id"],
            "username": user["username"],
            "role": user["role"],
            "full_name": user.get("full_name"),
        },
    )


@router.post("/login", response_model=TokenResponse)
def login_json(
    body: LoginRequest,
    db: Database = Depends(get_db),
):
    """Authenticate with JSON payload containing username and password."""
    return _authenticate_and_issue_tokens(body.username, body.password, db)


@router.post("/token", response_model=TokenResponse)
def login_oauth2_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Database = Depends(get_db),
):
    """Authenticate via OAuth2 Password Grant Form (used by OpenAPI / Swagger UI)."""
    return _authenticate_and_issue_tokens(form_data.username, form_data.password, db)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    payload_body: RefreshTokenRequest,
    db: Database = Depends(get_db),
):
    """Rotate refresh token and issue a fresh access and refresh token pair."""
    token_str = payload_body.refresh_token
    payload = decode_token(token_str)
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type; refresh token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    jti = payload.get("jti")
    exp_ts = payload.get("exp")
    user_repo = UserRepository(db)
    audit_repo = AuditRepository(db)

    if jti and user_repo.is_token_revoked(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    user = user_repo.get_by_id(user_id) if user_id else None
    if not user or not user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or deactivated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Invalidate the used refresh token (rotation policy)
    if jti and exp_ts:
        user_repo.revoke_token(jti, "refresh", datetime.fromtimestamp(exp_ts, tz=UTC))

    new_access_token, _, access_exp = create_access_token(user["id"], user["username"], user["role"])
    new_refresh_token, _, _ = create_refresh_token(user["id"], user["username"])

    audit_repo.record(
        actor=user["id"],
        action="auth.token_refreshed",
        subject_type="user",
        subject_id=user["id"],
    )

    expires_in = int((access_exp - datetime.now(UTC)).total_seconds())

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=expires_in if expires_in > 0 else ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "id": user["id"],
            "username": user["username"],
            "role": user["role"],
            "full_name": user.get("full_name"),
        },
    )


@router.post("/logout")
def logout(
    revoke_req: RevokeTokenRequest | None = None,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    """Revoke the current access token and optionally an associated refresh token."""
    user_repo = UserRepository(db)
    audit_repo = AuditRepository(db)

    access_jti = current_user.get("_token_jti")
    access_exp = current_user.get("_token_exp")
    if access_jti and access_exp:
        exp_dt = datetime.fromtimestamp(access_exp, tz=UTC)
        user_repo.revoke_token(access_jti, "access", exp_dt)

    if revoke_req and revoke_req.token:
        try:
            payload = decode_token(revoke_req.token)
            ref_jti = payload.get("jti")
            ref_exp = payload.get("exp")
            if ref_jti and ref_exp:
                user_repo.revoke_token(ref_jti, payload.get("type", "refresh"), datetime.fromtimestamp(ref_exp, tz=UTC))
        except HTTPException:
            pass  # If refresh token is already expired/invalid, revocation is a no-op

    audit_repo.record(
        actor=current_user["id"],
        action="auth.logout",
        subject_type="user",
        subject_id=current_user["id"],
    )

    return {"status": "logged_out"}


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: dict = Depends(get_current_user),
):
    """Return the profile and role of the currently authenticated user."""
    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        role=current_user["role"],
        full_name=current_user.get("full_name"),
        is_active=current_user["is_active"],
        created_at=str(current_user["created_at"]),
        updated_at=str(current_user["updated_at"]),
    )

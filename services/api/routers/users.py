"""User management endpoints for administrators and self-service profile updates."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from sbh.storage import (
    DB_INTEGRITY_ERRORS,
    AuditRepository,
    Database,
    UserRepository,
    UserValidationError,
)

from ..auth import get_current_user, hash_password, require_admin
from ..deps import get_db
from ..schemas import UserCreateRequest, UserListResponse, UserResponse, UserUpdateRequest

router = APIRouter(prefix="/users", tags=["Users & Access Control"])


@router.get("", response_model=UserListResponse)
def list_users(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    _: dict = Depends(require_admin),
    db: Database = Depends(get_db),
):
    """List users in the system (Admin only)."""
    repo = UserRepository(db)
    users = repo.list_users(limit=limit, offset=offset)
    total = repo.count_users()
    return UserListResponse(
        users=[
            UserResponse(
                id=u["id"],
                username=u["username"],
                role=u["role"],
                full_name=u.get("full_name"),
                is_active=bool(u["is_active"]),
                created_at=str(u["created_at"]),
                updated_at=str(u["updated_at"]),
            )
            for u in users
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    req: UserCreateRequest,
    current_admin: dict = Depends(require_admin),
    db: Database = Depends(get_db),
):
    """Create a new user account (Admin only)."""
    user_repo = UserRepository(db)
    audit_repo = AuditRepository(db)

    hashed = hash_password(req.password)
    try:
        user = user_repo.create_user(
            username=req.username,
            hashed_password=hashed,
            role=req.role,
            full_name=req.full_name,
        )
    except UserValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except DB_INTEGRITY_ERRORS as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with username '{req.username}' already exists",
        ) from exc

    audit_repo.record(
        actor=current_admin["id"],
        action="user.create",
        subject_type="user",
        subject_id=user["id"],
        details={"username": user["username"], "role": user["role"]},
    )

    return UserResponse(
        id=user["id"],
        username=user["username"],
        role=user["role"],
        full_name=user.get("full_name"),
        is_active=user["is_active"],
        created_at=str(user["created_at"]),
        updated_at=str(user["updated_at"]),
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    """Get a user by ID (Admin or self)."""
    if current_user["role"] != "admin" and current_user["id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot inspect other user profiles without admin privileges",
        )

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User '{user_id}' not found")

    return UserResponse(
        id=user["id"],
        username=user["username"],
        role=user["role"],
        full_name=user.get("full_name"),
        is_active=bool(user["is_active"]),
        created_at=str(user["created_at"]),
        updated_at=str(user["updated_at"]),
    )


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    req: UserUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    """Update user attributes (Admin or self). Non-admins cannot alter role or is_active."""
    is_admin = current_user["role"] == "admin"
    is_self = current_user["id"] == user_id

    if not is_admin and not is_self:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify other user profiles without admin privileges",
        )

    if not is_admin:
        if req.role is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Non-administrators cannot change account roles",
            )
        if req.is_active is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Non-administrators cannot modify account activation state",
            )

    user_repo = UserRepository(db)
    audit_repo = AuditRepository(db)

    hashed_pw = hash_password(req.password) if req.password else None

    try:
        updated = user_repo.update_user(
            user_id,
            full_name=req.full_name,
            role=req.role,
            is_active=req.is_active,
            hashed_password=hashed_pw,
        )
    except UserValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User '{user_id}' not found")

    audit_repo.record(
        actor=current_user["id"],
        action="user.update",
        subject_type="user",
        subject_id=user_id,
        details={"updated_fields": [k for k, v in req.model_dump().items() if v is not None]},
    )

    return UserResponse(
        id=updated["id"],
        username=updated["username"],
        role=updated["role"],
        full_name=updated.get("full_name"),
        is_active=bool(updated["is_active"]),
        created_at=str(updated["created_at"]),
        updated_at=str(updated["updated_at"]),
    )


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(
    user_id: str,
    current_admin: dict = Depends(require_admin),
    db: Database = Depends(get_db),
):
    """Delete a user account (Admin only). Users cannot delete their own account."""
    if current_admin["id"] == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Administrators cannot delete their own active account",
        )

    user_repo = UserRepository(db)
    audit_repo = AuditRepository(db)

    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User '{user_id}' not found")

    user_repo.delete_user(user_id)

    audit_repo.record(
        actor=current_admin["id"],
        action="user.delete",
        subject_type="user",
        subject_id=user_id,
        details={"username": user["username"]},
    )

    return {"status": "deleted", "user_id": user_id, "username": user["username"]}

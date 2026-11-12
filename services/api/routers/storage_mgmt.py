"""FastAPI router for local storage directory statistics, retention pruning, and database backups."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from services.api.schemas import (
    CreateBackupRequest,
    DatabaseBackupItem,
    DatabaseBackupListResponse,
    StorageDirectoryItem,
    StoragePruneReportItem,
    StoragePruneRequest,
    StoragePruneResponse,
    StorageStatsResponse,
    VerifyBackupRequest,
    VerifyBackupResponse,
)

from sbh.storage.backup import DatabaseBackupEngine
from sbh.storage.db_verify import verify_backup_integrity
from sbh.storage.fs import LocalStorageManager, StorageCategory
from sbh.storage.retention_engine import RetentionPolicy, StorageRetentionEngine

from ..auth import get_current_user

router = APIRouter(prefix="/storage", tags=["Storage & Backups"])


@router.get(
    "/stats",
    response_model=StorageStatsResponse,
    summary="Get storage consumption breakdown across snapshots, models, exports, and backups",
)
def get_storage_stats(
    _current_user: Annotated[dict, Depends(get_current_user)],
) -> StorageStatsResponse:
    mgr = LocalStorageManager()
    cat_items: dict[str, StorageDirectoryItem] = {}
    total_files = 0
    total_bytes = 0

    for cat in StorageCategory:
        st = mgr.get_directory_stats(cat)
        cat_items[cat.value] = StorageDirectoryItem(**st.to_dict())
        total_files += st.file_count
        total_bytes += st.total_bytes

    total_mb = round(total_bytes / (1024 * 1024), 2)
    return StorageStatsResponse(
        categories=cat_items,
        total_files=total_files,
        total_mb=total_mb,
    )


@router.post(
    "/prune",
    response_model=StoragePruneResponse,
    summary="Trigger retention policy prune across local storage categories",
)
def trigger_storage_prune(
    req: StoragePruneRequest,
    _current_user: Annotated[dict, Depends(get_current_user)],
) -> StoragePruneResponse:
    mgr = LocalStorageManager()
    engine = StorageRetentionEngine(mgr)
    policy = RetentionPolicy(
        max_age_days=req.max_age_days,
        max_directory_bytes=int(req.max_size_mb * 1024 * 1024) if req.max_size_mb else None,
        keep_minimum_count=req.keep_minimum,
    )

    if req.category:
        try:
            cat = StorageCategory(req.category)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=f"Invalid category: {req.category}") from exc
        reports = [engine.prune_category(cat, policy, dry_run=req.dry_run)]
    else:
        reports = engine.prune_all({cat: policy for cat in StorageCategory}, dry_run=req.dry_run)

    return StoragePruneResponse(
        reports=[StoragePruneReportItem(**r.to_dict()) for r in reports]
    )


@router.get(
    "/backups",
    response_model=DatabaseBackupListResponse,
    summary="List completed database backups with checksums and table counts",
)
def list_database_backups(
    _current_user: Annotated[dict, Depends(get_current_user)],
) -> DatabaseBackupListResponse:
    engine = DatabaseBackupEngine()
    backups = engine.list_backups()
    return DatabaseBackupListResponse(
        backups=[DatabaseBackupItem(**b.to_dict()) for b in backups]
    )


@router.post(
    "/backups",
    response_model=DatabaseBackupItem,
    status_code=status.HTTP_201_CREATED,
    summary="Create an atomic backup of active database",
)
def create_database_backup(
    req: CreateBackupRequest,
    _current_user: Annotated[dict, Depends(get_current_user)],
) -> DatabaseBackupItem:
    engine = DatabaseBackupEngine()
    db_p = Path.cwd() / "sbh-dev.sqlite"
    if not db_p.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active SQLite database not found on disk",
        )
    try:
        _, meta = engine.backup_sqlite(
            db_p,
            output_filename=req.output_filename,
            compress=req.compress,
            notes=req.notes,
        )
        return DatabaseBackupItem(**meta.to_dict())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Backup failed: {exc}") from exc


@router.post(
    "/backups/verify",
    response_model=VerifyBackupResponse,
    summary="Verify cryptographic integrity of a database backup artifact",
)
def verify_database_backup(
    req: VerifyBackupRequest,
    _current_user: Annotated[dict, Depends(get_current_user)],
) -> VerifyBackupResponse:
    mgr = LocalStorageManager()
    target = mgr.get_category_dir(StorageCategory.BACKUPS) / req.backup_id
    if not target.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Backup artifact not found: {req.backup_id}",
        )
    ok, msg = verify_backup_integrity(target)
    return VerifyBackupResponse(
        backup_id=req.backup_id,
        is_valid=ok,
        message=msg,
    )

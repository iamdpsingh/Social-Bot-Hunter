"""Dataset import and investigation creation endpoints."""

from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status

from sbh.config import Config
from sbh.contracts.capabilities import default_registry
from sbh.fixtures import synthetic
from sbh.pipeline.run import import_dataset
from sbh.shared.errors import ScanFailedError
from sbh.storage import AuditRepository, Database, sync_registry

from ..auth import require_investigator
from ..deps import get_config, get_db
from ..schemas import ImportDatasetRequest, ImportResponse

router = APIRouter(prefix="/imports", tags=["Imports & Ingestion"])


@router.post("/synthetic-demo", response_model=ImportResponse)
def run_synthetic_demo(
    seed: int = Query(42),
    current_user: dict = Depends(require_investigator),
    db: Database = Depends(get_db),
    cfg: Config = Depends(get_config),
):
    """Generate and ingest a deterministic synthetic dataset for pipeline validation (Investigator/Admin only)."""
    sync_registry(db, default_registry())
    audit_repo = AuditRepository(db)

    with tempfile.TemporaryDirectory() as tmp_dir:
        ds = synthetic.generate(seed)
        out_path = synthetic.write_csv_dir(ds, Path(tmp_dir) / "demo")
        try:
            res = import_dataset(db, str(out_path), cfg, requested_by=current_user["username"])
        except ScanFailedError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"scan_id": exc.scan_id, "reason": exc.reason},
            ) from exc

        audit_repo.record(
            actor=current_user["id"],
            action="demo.import",
            subject_type="scan",
            subject_id=res.scan_id,
            details={"seed": seed, "status": res.status},
        )

        return ImportResponse(
            status=res.status,
            scan_id=res.scan_id,
            already_imported=res.already_imported,
            summary=res.summary,
            is_synthetic=True,
        )


@router.post("/dataset", response_model=ImportResponse)
def import_dataset_endpoint(
    req: ImportDatasetRequest,
    current_user: dict = Depends(require_investigator),
    db: Database = Depends(get_db),
    cfg: Config = Depends(get_config),
):
    """Import a local verified dataset directory into the investigation pipeline (Investigator/Admin only)."""
    source = Path(req.source_path)
    if not source.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source path '{req.source_path}' does not exist on server",
        )

    sync_registry(db, default_registry())
    audit_repo = AuditRepository(db)

    try:
        res = import_dataset(
            db,
            str(source),
            cfg,
            requested_by=current_user["username"],
            allow_resume_running=req.allow_resume_running,
        )
    except ScanFailedError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"scan_id": exc.scan_id, "reason": exc.reason},
        ) from exc

    audit_repo.record(
        actor=current_user["id"],
        action="dataset.import",
        subject_type="scan",
        subject_id=res.scan_id,
        details={"source_path": req.source_path, "status": res.status},
    )

    return ImportResponse(
        status=res.status,
        scan_id=res.scan_id,
        already_imported=res.already_imported,
        summary=res.summary,
        is_synthetic=False,
    )


@router.post(
    "/archive",
    response_model=ArchiveImportResponse,
    summary="Upload and inspect/ingest social media dataset archive",
)
async def upload_and_import_archive(
    file: UploadFile = File(...),
    current_user: dict = Depends(require_investigator),
    db: Database = Depends(get_db),
    cfg: Config = Depends(get_config),
) -> ArchiveImportResponse:
    """Upload and securely inspect ZIP/TAR archives, checking for zip-bombs and traversals."""
    sync_registry(db, default_registry())
    audit_repo = AuditRepository(db)
    with tempfile.NamedTemporaryFile(delete=False, suffix=f'_{file.filename}') as tmp_file:
        tmp_archive_path = Path(tmp_file.name)
        try:
            while chunk := await file.read(1024 * 1024):
                tmp_file.write(chunk)
            tmp_file.flush()
        except Exception as exc:
            tmp_archive_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to receive uploaded archive file: {exc}",
            ) from exc
    try:
        result = extract_and_detect_archive(tmp_archive_path)
    except ArchiveSecurityError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "security_violation", "message": str(exc)},
        ) from exc
    except ArchiveFormatError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "invalid_format", "message": str(exc)},
        # format error branch
        ) from exc
    finally:
        tmp_archive_path.unlink(missing_ok=True)

    audit_repo.record(
        actor=current_user["id"],
        action="archive.upload",
        # recorded in security audit journal
        subject_type="archive",
        subject_id=file.filename or "unknown",
        details={
            "filename": file.filename,
            "format": result.format.value,
            "file_count": result.file_count,
            "total_uncompressed_bytes": result.total_uncompressed_bytes,
            "platform_hint": result.platform_hint,
        },
    )

    return ArchiveImportResponse(
        status="extracted",
        archive_format=result.format.value,
        file_count=result.file_count,
        uncompressed_bytes=result.total_uncompressed_bytes,
        platform_detected=result.platform_hint,
        records_file=str(result.records_path) if result.records_path else None,
        extracted_path=str(result.extracted_path),
        message=f"Archive safely unpacked with {result.file_count} files ({result.format.value})",
    )

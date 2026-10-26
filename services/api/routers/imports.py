"""Dataset import and investigation creation endpoints."""

import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sbh.config import Config
from sbh.contracts.capabilities import default_registry
from sbh.fixtures import synthetic
from sbh.pipeline.run import import_dataset
from sbh.shared.errors import ScanFailedError
from sbh.storage import Database, sync_registry

from ..deps import get_config, get_db

router = APIRouter(prefix="/imports", tags=["Imports & Ingestion"])


class ImportRequest(BaseModel):
    source_path: str
    requested_by: str = "api-user"
    allow_resume_running: bool = False


@router.post("/synthetic-demo")
def run_synthetic_demo(
    seed: int = Query(42),
    requested_by: str = Query("api-user"),
    db: Database = Depends(get_db),
    cfg: Config = Depends(get_config),
):
    sync_registry(db, default_registry())
    with tempfile.TemporaryDirectory() as tmp_dir:
        ds = synthetic.generate(seed)
        out_path = synthetic.write_csv_dir(ds, Path(tmp_dir) / "demo")
        try:
            res = import_dataset(db, str(out_path), cfg, requested_by=requested_by)
        except ScanFailedError as exc:
            raise HTTPException(status_code=400, detail={"scan_id": exc.scan_id, "reason": exc.reason})

        return {
            "status": res.status,
            "scan_id": res.scan_id,
            "already_imported": res.already_imported,
            "summary": res.summary,
            "is_synthetic": True,
        }


@router.post("/dataset")
def import_dataset_endpoint(
    req: ImportRequest,
    db: Database = Depends(get_db),
    cfg: Config = Depends(get_config),
):
    source = Path(req.source_path)
    if not source.exists():
        raise HTTPException(status_code=404, detail=f"Source path '{req.source_path}' does not exist on server")

    sync_registry(db, default_registry())
    try:
        res = import_dataset(db, str(source), cfg, requested_by=req.requested_by, allow_resume_running=req.allow_resume_running)
    except ScanFailedError as exc:
        raise HTTPException(status_code=400, detail={"scan_id": exc.scan_id, "reason": exc.reason})

    return {
        "status": res.status,
        "scan_id": res.scan_id,
        "already_imported": res.already_imported,
        "summary": res.summary,
    }

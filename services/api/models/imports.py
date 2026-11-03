"""Dataset import schemas."""

from __future__ import annotations

from pydantic import BaseModel


class DatasetImportRequest(BaseModel):
    """Request to import pre-packaged synthetic dataset."""

    dataset_name: str = "synthetic-demo"


class DatasetImportResponse(BaseModel):
    """Import execution result."""

    status: str
    scan_id: str
    dataset_name: str
    accounts_imported: int
    edges_imported: int

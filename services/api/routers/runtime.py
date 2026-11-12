"""FastAPI router for local runtime status, supervisor telemetry, and worker queue."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from ..auth import get_current_user
from services.api.schemas import (
    EnqueueJobRequest,
    EnqueueJobResponse,
    EnvCheckResponse,
    RuntimeStatusResponse,
    WorkerJobItem,
)

from sbh.runtime.env_validator import validate_local_runtime_environment
from sbh.runtime.job import JobPriority
from sbh.runtime.queue import PersistentJobQueue
from sbh.runtime.supervisor import LocalSupervisor

router = APIRouter(prefix="/runtime", tags=["Runtime Orchestration"])


@router.get(
    "/status",
    response_model=RuntimeStatusResponse,
    summary="Get multi-service supervisor and system resource telemetry",
)
def get_runtime_status(
    _current_user: Annotated[dict, Depends(get_current_user)],
) -> RuntimeStatusResponse:
    supervisor = LocalSupervisor()
    st = supervisor.get_status()
    return RuntimeStatusResponse(**st)


@router.get(
    "/env",
    response_model=EnvCheckResponse,
    summary="Validate local virtual environment and filesystem readiness",
)
def get_env_check(
    _current_user: Annotated[dict, Depends(get_current_user)],
    no_ports: bool = Query(False, description="Skip port availability checks"),
) -> EnvCheckResponse:
    rep = validate_local_runtime_environment(check_ports=not no_ports)
    return EnvCheckResponse(**rep.to_dict())


@router.get(
    "/worker/jobs",
    response_model=list[WorkerJobItem],
    summary="List background worker jobs",
)
def list_worker_jobs(
    _current_user: Annotated[dict, Depends(get_current_user)],
    status: str | None = Query(None, description="Filter jobs by status"),
    limit: int = Query(50, ge=1, le=200),
) -> list[WorkerJobItem]:
    queue = PersistentJobQueue()
    jobs = queue.list_jobs(status=status, limit=limit)
    return [WorkerJobItem(**j.to_dict()) for j in jobs]


@router.post(
    "/worker/jobs",
    response_model=EnqueueJobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enqueue a new background task",
)
def enqueue_worker_job(
    req: EnqueueJobRequest,
    _current_user: Annotated[dict, Depends(get_current_user)],
) -> EnqueueJobResponse:
    queue = PersistentJobQueue()
    try:
        priority = JobPriority(req.priority)
    except ValueError:
        priority = JobPriority.NORMAL

    job = queue.enqueue(
        task_type=req.task_type,
        payload=req.payload,
        priority=priority,
        max_attempts=req.max_attempts,
    )
    return EnqueueJobResponse(
        job_id=job.job_id,
        task_type=job.task_type,
        status=job.status,
        priority=job.priority,
        created_at=job.created_at,
    )


@router.get(
    "/worker/jobs/{job_id}",
    response_model=WorkerJobItem,
    summary="Get status and payload of a specific background job",
)
def get_worker_job(
    job_id: str,
    _current_user: Annotated[dict, Depends(get_current_user)],
) -> WorkerJobItem:
    queue = PersistentJobQueue()
    job = queue.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job not found: {job_id}",
        )
    return WorkerJobItem(**job.to_dict())

import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundException
from app.database import get_db
from app.models.user import User
from app.schemas.job import (
    ExecuteJobRequest,
    ExecuteJobResponse,
    JobDetailResponse,
    JobResponse,
)
from app.services import job_service

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/execute", response_model=ExecuteJobResponse, status_code=202)
async def execute_job(
    body: ExecuteJobRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    operations = [op.model_dump() for op in body.operations]
    job = await job_service.create_and_execute_job(
        db, user.id, body.image_id, operations, body.pipeline_id
    )
    return ExecuteJobResponse(job_id=job.id)


@router.get("", response_model=list[JobResponse])
async def list_jobs(
    limit: int = 50,
    offset: int = 0,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await job_service.list_jobs(db, user.id, limit, offset)


@router.get("/{job_id}", response_model=JobDetailResponse)
async def get_job(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await job_service.get_job(db, job_id, user.id)


@router.get("/{job_id}/steps/{step_number}/image")
async def get_step_image(
    job_id: uuid.UUID,
    step_number: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    job = await job_service.get_job(db, job_id, user.id)
    for step in job.steps:
        if step.step_number == step_number and step.result_image_path:
            return FileResponse(step.result_image_path, media_type="image/png")
    raise NotFoundException("Step image")


@router.delete("/{job_id}", status_code=204)
async def delete_job(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await job_service.delete_job(db, job_id, user.id)

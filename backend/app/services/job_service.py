import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.core.exceptions import ForbiddenException, NotFoundException
from app.engine.registry import OperationRegistry
from app.models.job import Job, JobStatus
from app.models.job_step import JobStep
from app.workers.tasks import execute_pipeline

import app.engine.operations  # noqa: F401


async def create_and_execute_job(
    db: AsyncSession,
    user_id: uuid.UUID,
    image_id: uuid.UUID,
    operations: list[dict],
    pipeline_id: uuid.UUID | None = None,
) -> Job:
    for op in operations:
        if not OperationRegistry.has(op["type"]):
            raise ValueError(f"Unknown operation: {op['type']}")
    if len(operations) > settings.MAX_PIPELINE_OPERATIONS:
        raise ValueError(f"Max {settings.MAX_PIPELINE_OPERATIONS} operations allowed")

    job = Job(
        user_id=user_id,
        image_id=image_id,
        pipeline_id=pipeline_id,
        total_steps=len(operations),
        status=JobStatus.PENDING,
    )
    db.add(job)
    await db.flush()

    for i, op in enumerate(operations):
        step = JobStep(
            job_id=job.id,
            step_number=i + 1,
            operation_type=op["type"],
            operation_params=op.get("params", {}),
        )
        db.add(step)
    await db.flush()

    execute_pipeline.delay(str(job.id))
    return job


async def get_job(db: AsyncSession, job_id: uuid.UUID, user_id: uuid.UUID) -> Job:
    result = await db.execute(select(Job).options(selectinload(Job.steps)).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise NotFoundException("Job")
    if job.user_id != user_id:
        raise ForbiddenException()
    return job


async def list_jobs(db: AsyncSession, user_id: uuid.UUID, limit: int = 50, offset: int = 0) -> list[Job]:
    result = await db.execute(
        select(Job).where(Job.user_id == user_id).order_by(Job.created_at.desc()).limit(limit).offset(offset)
    )
    return list(result.scalars().all())


async def delete_job(db: AsyncSession, job_id: uuid.UUID, user_id: uuid.UUID) -> None:
    job = await get_job(db, job_id, user_id)
    from app.services.storage_service import delete_directory, get_results_dir

    delete_directory(get_results_dir(job.id))
    await db.delete(job)

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.pipeline import Pipeline


async def create_pipeline(
    db: AsyncSession,
    user_id: uuid.UUID,
    name: str,
    operations: list[dict],
    description: str | None = None,
) -> Pipeline:
    pipeline = Pipeline(user_id=user_id, name=name, description=description, operations=operations)
    db.add(pipeline)
    await db.flush()
    return pipeline


async def get_pipeline(db: AsyncSession, pipeline_id: uuid.UUID, user_id: uuid.UUID) -> Pipeline:
    result = await db.execute(select(Pipeline).where(Pipeline.id == pipeline_id))
    pipeline = result.scalar_one_or_none()
    if not pipeline:
        raise NotFoundException("Pipeline")
    if pipeline.user_id != user_id:
        raise ForbiddenException()
    return pipeline


async def list_pipelines(db: AsyncSession, user_id: uuid.UUID) -> list[Pipeline]:
    result = await db.execute(
        select(Pipeline).where(Pipeline.user_id == user_id).order_by(Pipeline.updated_at.desc())
    )
    return list(result.scalars().all())


async def update_pipeline(
    db: AsyncSession,
    pipeline_id: uuid.UUID,
    user_id: uuid.UUID,
    name: str | None = None,
    description: str | None = None,
    operations: list[dict] | None = None,
) -> Pipeline:
    pipeline = await get_pipeline(db, pipeline_id, user_id)
    if name is not None:
        pipeline.name = name
    if description is not None:
        pipeline.description = description
    if operations is not None:
        pipeline.operations = operations
    await db.flush()
    return pipeline


async def delete_pipeline(db: AsyncSession, pipeline_id: uuid.UUID, user_id: uuid.UUID) -> None:
    pipeline = await get_pipeline(db, pipeline_id, user_id)
    await db.delete(pipeline)

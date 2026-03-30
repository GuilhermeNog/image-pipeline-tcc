import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.pipeline import (
    CreatePipelineRequest,
    PipelineResponse,
    UpdatePipelineRequest,
)
from app.services import pipeline_service

router = APIRouter(prefix="/pipelines", tags=["pipelines"])


@router.get("", response_model=list[PipelineResponse])
async def list_pipelines(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await pipeline_service.list_pipelines(db, user.id)


@router.post("", response_model=PipelineResponse, status_code=201)
async def create_pipeline(
    body: CreatePipelineRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ops = [op.model_dump() for op in body.operations]
    return await pipeline_service.create_pipeline(
        db, user.id, body.name, ops, body.description
    )


@router.get("/{pipeline_id}", response_model=PipelineResponse)
async def get_pipeline(
    pipeline_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await pipeline_service.get_pipeline(db, pipeline_id, user.id)


@router.put("/{pipeline_id}", response_model=PipelineResponse)
async def update_pipeline(
    pipeline_id: uuid.UUID,
    body: UpdatePipelineRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ops = [op.model_dump() for op in body.operations] if body.operations else None
    return await pipeline_service.update_pipeline(
        db, pipeline_id, user.id, body.name, body.description, ops
    )


@router.delete("/{pipeline_id}", status_code=204)
async def delete_pipeline(
    pipeline_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await pipeline_service.delete_pipeline(db, pipeline_id, user.id)

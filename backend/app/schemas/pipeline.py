import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class PipelineOperationInput(BaseModel):
    type: str
    params: dict = Field(default_factory=dict)


class CreatePipelineRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    operations: list[PipelineOperationInput] = Field(min_length=1, max_length=20)


class UpdatePipelineRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    operations: list[PipelineOperationInput] | None = None


class PipelineResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    description: str | None
    operations: list
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

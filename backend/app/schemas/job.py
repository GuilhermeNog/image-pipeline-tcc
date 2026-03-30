import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class OperationInput(BaseModel):
    type: str
    params: dict = Field(default_factory=dict)


class ExecuteJobRequest(BaseModel):
    image_id: uuid.UUID
    pipeline_id: uuid.UUID | None = None
    operations: list[OperationInput] = Field(min_length=1, max_length=20)


class JobStepResponse(BaseModel):
    id: uuid.UUID
    step_number: int
    operation_type: str
    operation_params: dict
    result_image_path: str | None
    processing_time_ms: int | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class JobResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    pipeline_id: uuid.UUID | None
    image_id: uuid.UUID
    status: str
    current_step: int
    total_steps: int
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class JobDetailResponse(JobResponse):
    steps: list[JobStepResponse] = []


class ExecuteJobResponse(BaseModel):
    job_id: uuid.UUID
    status: str = "pending"

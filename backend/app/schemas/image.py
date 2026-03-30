import uuid
from datetime import datetime

from pydantic import BaseModel


class ImageUploadResponse(BaseModel):
    id: uuid.UUID
    filename: str
    original_filename: str
    mime_type: str
    file_size: int
    width: int
    height: int
    created_at: datetime

    model_config = {"from_attributes": True}

import os
import uuid

import cv2
import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.image import Image
from app.services.storage_service import save_upload

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"}


async def upload_image(
    db: AsyncSession, user_id: uuid.UUID, filename: str, content_type: str, content: bytes
) -> Image:
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file format: {ext}")
    if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise ValueError(f"File too large. Max {settings.MAX_UPLOAD_SIZE_MB}MB")

    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = save_upload(user_id, unique_filename, content)

    nparr = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Invalid image file")

    height, width = img.shape[:2]

    image = Image(
        user_id=user_id,
        filename=unique_filename,
        original_filename=filename,
        file_path=file_path,
        mime_type=content_type or "image/png",
        file_size=len(content),
        width=width,
        height=height,
    )
    db.add(image)
    await db.flush()
    return image


async def get_image(db: AsyncSession, image_id: uuid.UUID, user_id: uuid.UUID) -> Image:
    result = await db.execute(select(Image).where(Image.id == image_id))
    image = result.scalar_one_or_none()
    if not image:
        raise NotFoundException("Image")
    if image.user_id != user_id:
        raise ForbiddenException()
    return image


async def delete_image(db: AsyncSession, image_id: uuid.UUID, user_id: uuid.UUID) -> None:
    image = await get_image(db, image_id, user_id)
    from app.services.storage_service import delete_file

    delete_file(image.file_path)
    await db.delete(image)

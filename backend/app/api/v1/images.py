import uuid

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.image import ImageUploadResponse
from app.services import image_service

router = APIRouter(prefix="/images", tags=["images"])


@router.post("/upload", response_model=ImageUploadResponse, status_code=201)
async def upload_image(
    file: UploadFile,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    content = await file.read()
    image = await image_service.upload_image(
        db, user.id, file.filename or "image.png", file.content_type, content
    )
    return image


@router.get("/{image_id}", response_model=ImageUploadResponse)
async def get_image(
    image_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await image_service.get_image(db, image_id, user.id)


@router.delete("/{image_id}", status_code=204)
async def delete_image(
    image_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await image_service.delete_image(db, image_id, user.id)


@router.get("/file/{image_id}")
async def serve_image(
    image_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    image = await image_service.get_image(db, image_id, user.id)
    return FileResponse(image.file_path, media_type=image.mime_type)

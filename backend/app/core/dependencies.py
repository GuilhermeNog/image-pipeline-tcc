import uuid

from fastapi import Cookie, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import TokenInvalidException
from app.core.security import decode_token
from app.database import get_db
from app.models.user import User


async def get_current_user(
    request: Request,
    access_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = access_token
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]

    if not token:
        raise TokenInvalidException()

    try:
        payload = decode_token(token, token_type="access")
    except ValueError:
        raise TokenInvalidException()

    user_id = payload.get("sub")
    if not user_id:
        raise TokenInvalidException()

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise TokenInvalidException()

    return user


async def get_current_active_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_active:
        raise TokenInvalidException()
    return user

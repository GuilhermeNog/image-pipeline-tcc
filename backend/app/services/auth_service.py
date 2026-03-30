import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import (
    AccountLockedException,
    EmailAlreadyExistsException,
    InvalidCredentialsException,
    TokenInvalidException,
)
from app.core.security import decode_token, hash_password, verify_password
from app.models.user import User
from app.services.token_service import (
    create_token_pair,
    find_valid_refresh_token,
    hash_token,
    revoke_all_user_tokens,
    revoke_refresh_token,
)


async def register(db: AsyncSession, name: str, email: str, password: str) -> tuple[User, str, str]:
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        raise EmailAlreadyExistsException()

    verification_code = "".join([str(secrets.randbelow(10)) for _ in range(6)])

    user = User(
        name=name,
        email=email,
        password=hash_password(password),
        email_verification_token=verification_code,
        email_verification_expires=datetime.now(timezone.utc) + timedelta(minutes=settings.EMAIL_VERIFICATION_EXPIRY_MINUTES),
    )
    db.add(user)
    await db.flush()

    access_token, refresh_token = await create_token_pair(db, user.id)
    return user, access_token, refresh_token


async def login(
    db: AsyncSession,
    email: str,
    password: str,
    user_agent: str | None = None,
    ip_address: str | None = None,
) -> tuple[User, str, str]:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise InvalidCredentialsException()

    if user.locked_until and user.locked_until > datetime.now(timezone.utc):
        raise AccountLockedException(locked_until=user.locked_until.isoformat())

    if not verify_password(password, user.password):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= settings.ACCOUNT_LOCKOUT_ATTEMPTS:
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCOUNT_LOCKOUT_MINUTES)
        await db.flush()
        raise InvalidCredentialsException()

    user.failed_login_attempts = 0
    user.locked_until = None
    await db.flush()

    access_token, refresh_token = await create_token_pair(db, user.id, user_agent, ip_address)
    return user, access_token, refresh_token


async def refresh(db: AsyncSession, raw_refresh_token: str, user_agent: str | None = None, ip_address: str | None = None) -> tuple[str, str]:
    try:
        payload = decode_token(raw_refresh_token, token_type="refresh")
    except ValueError:
        raise TokenInvalidException()

    token_hash = hash_token(raw_refresh_token)
    db_token = await find_valid_refresh_token(db, token_hash)
    if not db_token:
        raise TokenInvalidException()

    await revoke_refresh_token(db, token_hash)

    user_id = payload["sub"]
    access_token, new_refresh_token = await create_token_pair(db, user_id, user_agent, ip_address)
    return access_token, new_refresh_token


async def logout(db: AsyncSession, raw_refresh_token: str) -> None:
    token_hash = hash_token(raw_refresh_token)
    await revoke_refresh_token(db, token_hash)


async def logout_all(db: AsyncSession, user_id) -> None:
    await revoke_all_user_tokens(db, user_id)


async def verify_email(db: AsyncSession, user: User, code: str) -> None:
    if user.email_verified:
        return
    if user.email_verification_token != code:
        raise TokenInvalidException()
    if user.email_verification_expires and user.email_verification_expires < datetime.now(timezone.utc):
        raise TokenInvalidException()
    user.email_verified = True
    user.email_verification_token = None
    user.email_verification_expires = None
    await db.flush()


async def resend_verification(db: AsyncSession, user: User) -> str:
    code = "".join([str(secrets.randbelow(10)) for _ in range(6)])
    user.email_verification_token = code
    user.email_verification_expires = datetime.now(timezone.utc) + timedelta(minutes=settings.EMAIL_VERIFICATION_EXPIRY_MINUTES)
    await db.flush()
    return code


async def forgot_password(db: AsyncSession, email: str) -> str | None:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        return None

    token = secrets.token_urlsafe(32)
    user.password_reset_token = token
    user.password_reset_expires = datetime.now(timezone.utc) + timedelta(minutes=settings.PASSWORD_RESET_EXPIRY_MINUTES)
    await db.flush()
    return token


async def reset_password(db: AsyncSession, email: str, token: str, new_password: str) -> None:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or user.password_reset_token != token:
        raise TokenInvalidException()
    if user.password_reset_expires and user.password_reset_expires < datetime.now(timezone.utc):
        raise TokenInvalidException()

    user.password = hash_password(new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    user.failed_login_attempts = 0
    user.locked_until = None
    await db.flush()

    await revoke_all_user_tokens(db, user.id)

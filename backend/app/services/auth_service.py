import hashlib
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User


def _hash_token(raw: str) -> str:
    """SHA-256 hash of a raw refresh token string."""
    return hashlib.sha256(raw.encode()).hexdigest()


async def register_user(
    db: AsyncSession,
    email: str,
    password: str,
    full_name: str,
) -> User:
    email = email.lower()

    existing = await db.execute(select(User).where(User.email == email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"detail": "Email already registered", "code": "AUTH_EMAIL_EXISTS"},
        )

    user = User(
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def login_user(db: AsyncSession, email: str, password: str) -> User:
    email = email.lower()
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    # Same message for missing user OR wrong password — no enumeration
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"detail": "Invalid credentials", "code": "AUTH_INVALID_CREDENTIALS"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"detail": "Account is disabled", "code": "AUTH_INVALID_CREDENTIALS"},
        )

    return user


async def create_token_pair(db: AsyncSession, user_id: int) -> dict:
    access_token = create_access_token(user_id)
    raw_refresh = create_refresh_token(user_id)

    expires_at = datetime.utcnow() + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    record = RefreshToken(
        user_id=user_id,
        token_hash=_hash_token(raw_refresh),
        expires_at=expires_at,
    )
    db.add(record)
    await db.commit()

    return {"access_token": access_token, "refresh_token": raw_refresh}


async def refresh_token_pair(db: AsyncSession, raw_refresh_token: str) -> dict:
    token_hash = _hash_token(raw_refresh_token)

    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    record = result.scalar_one_or_none()

    if (
        not record
        or record.revoked
        or record.expires_at < datetime.utcnow()
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"detail": "Invalid or expired refresh token", "code": "AUTH_TOKEN_INVALID"},
        )

    # Rotate: revoke old token immediately
    record.revoked = True
    await db.commit()

    return await create_token_pair(db, record.user_id)


async def logout_user(db: AsyncSession, raw_refresh_token: str) -> None:
    token_hash = _hash_token(raw_refresh_token)

    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    record = result.scalar_one_or_none()

    if record:
        record.revoked = True
        await db.commit()
    # If not found — silent success (idempotent logout)

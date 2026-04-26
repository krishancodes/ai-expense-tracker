"""
routers/users.py
────────────────
GET    /users/me → return current user as UserResponse        → 200
PUT    /users/me → update only provided fields                → 200
DELETE /users/me → soft-delete (is_active=False)              → 204

All routes require a valid JWT via Depends(get_current_user).
Logic is simple enough to live directly in the router.
"""

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UpdateUserRequest, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


# ── GET /users/me ──────────────────────────────────────────────────────────────

@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)


# ── PUT /users/me ──────────────────────────────────────────────────────────────

@router.put(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update current user profile",
    description="Only fields that are explicitly provided (non-null) will be updated.",
)
async def update_me(
    payload: UpdateUserRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    # Apply only the fields that were actually sent (exclude_unset drops omitted keys)
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(current_user, field, value)

    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return UserResponse.model_validate(current_user)


# ── DELETE /users/me ───────────────────────────────────────────────────────────

@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate current user account",
    description="Soft-deletes the account by setting is_active=False. No content is returned.",
)
async def delete_me(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    current_user.is_active = False
    db.add(current_user)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

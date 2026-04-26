"""
routers/insights.py
───────────────────
GET  /insights            → get_insights (query params: month, year)
POST /insights/regenerate → regenerate_insights (rate-limited: 10/hour per user)

Both routes require a valid JWT (Depends(get_current_user)).
Rate limiting is applied via slowapi using the authenticated user's ID as the key.
"""

from datetime import date
from typing import Union

from fastapi import APIRouter, Depends, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.insight import InsightError, InsightResponse
from app.services.insight_service import get_insights, regenerate_insights

# ── Rate limiter ───────────────────────────────────────────────────────────────
# Key on authenticated user ID so the limit is per-user, not per-IP.
def _user_id_key(request: Request) -> str:
    """Extract the authenticated user's ID from request.state (set by dependency)."""
    user: User | None = getattr(request.state, "current_user", None)
    if user is not None:
        return str(user.id)
    # Fallback to IP (should not happen on authenticated routes)
    return get_remote_address(request)


limiter = Limiter(key_func=_user_id_key, default_limits=[settings.AI_RATE_LIMIT])

router = APIRouter(prefix="/insights", tags=["insights"])


# ── GET /insights ──────────────────────────────────────────────────────────────

@router.get(
    "",
    response_model=Union[InsightResponse, InsightError],
    status_code=status.HTTP_200_OK,
    summary="Get AI-generated insights for a month",
    description=(
        "Returns cached insights if available (< 1 hour old), "
        "otherwise calls the LLM and caches the result."
    ),
)
async def insights_get(
    request: Request,
    month: int = date.today().month,
    year: int = date.today().year,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Union[InsightResponse, InsightError]:
    # Expose user to rate-limiter key function via request.state
    request.state.current_user = current_user
    return await get_insights(db, current_user.id, month, year)


# ── POST /insights/regenerate ──────────────────────────────────────────────────

@router.post(
    "/regenerate",
    response_model=Union[InsightResponse, InsightError],
    status_code=status.HTTP_200_OK,
    summary="Force-regenerate AI insights (rate-limited: 10/hour)",
    description=(
        "Deletes the cached row and re-calls the LLM. "
        "Rate-limited to 10 requests per hour per authenticated user."
    ),
)
@limiter.limit(settings.AI_RATE_LIMIT)
async def insights_regenerate(
    request: Request,
    month: int = date.today().month,
    year: int = date.today().year,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Union[InsightResponse, InsightError]:
    request.state.current_user = current_user
    return await regenerate_insights(db, current_user.id, month, year)

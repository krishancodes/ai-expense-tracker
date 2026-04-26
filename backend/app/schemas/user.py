from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    """Public user representation — hashed_password is never included."""

    id: int
    email: str
    full_name: str
    currency: str
    budget_reset_day: int
    created_at: datetime

    model_config = {"from_attributes": True}


class UpdateUserRequest(BaseModel):
    """All fields are optional; only provided fields will be updated."""

    full_name: Optional[str] = Field(
        default=None,
        min_length=2,
        description="Display name (minimum 2 characters)",
    )
    currency: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=3,
        description="ISO 4217 currency code, exactly 3 characters (e.g. USD, INR)",
    )
    budget_reset_day: Optional[int] = Field(
        default=None,
        ge=1,
        le=28,
        description="Day of month when the budget resets (1–28)",
    )

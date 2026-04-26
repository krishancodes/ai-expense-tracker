from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BudgetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    category_id: Optional[int]
    amount: Decimal
    month: int
    year: int
    # Computed fields — not stored in DB, populated by the service
    spent: float
    utilization_pct: float
    alert_80: bool
    alert_100: bool


class SetBudgetRequest(BaseModel):
    category_id: Optional[int] = None  # None = overall budget
    amount: Decimal = Field(..., gt=0)
    month: int = Field(..., ge=1, le=12)
    year: int

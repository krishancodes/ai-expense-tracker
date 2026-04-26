from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.expense import PaymentMethod


class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    category_id: int
    amount: Decimal
    date: date
    description: Optional[str]
    payment_method: PaymentMethod
    created_at: datetime


class CreateExpenseRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    category_id: int
    date: date
    description: Optional[str] = Field(default=None, max_length=200)
    payment_method: PaymentMethod

    @field_validator("date")
    @classmethod
    def date_not_in_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Expense date must not be in the future.")
        return v


class UpdateExpenseRequest(BaseModel):
    amount: Optional[Decimal] = Field(default=None, gt=0)
    category_id: Optional[int] = None
    date: Optional[date] = None
    description: Optional[str] = Field(default=None, max_length=200)
    payment_method: Optional[PaymentMethod] = None

    @field_validator("date")
    @classmethod
    def date_not_in_future(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v > date.today():
            raise ValueError("Expense date must not be in the future.")
        return v


class ExpenseListResponse(BaseModel):
    data: list[ExpenseResponse]
    total: int
    page: int
    limit: int


class ExpenseFilters(BaseModel):
    category_id: Optional[int] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    payment_method: Optional[PaymentMethod] = None
    search: Optional[str] = None
    page: int = 1
    limit: int = 20
    sort_by: str = "date"
    order: str = "desc"

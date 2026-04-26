from __future__ import annotations

from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.dependencies import get_current_user
from app.models.expense import PaymentMethod
from app.models.user import User
from app.schemas.expense import (
    CreateExpenseRequest,
    ExpenseListResponse,
    ExpenseResponse,
    UpdateExpenseRequest,
)
from app.services.expense_service import (
    ExpenseFilters,
    create_expense,
    delete_expense,
    get_expense_by_id,
    get_expenses,
    update_expense,
)

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.get("", response_model=ExpenseListResponse, status_code=status.HTTP_200_OK)
async def list_expenses(
    # --- filter params ---
    category_id: int | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    payment_method: PaymentMethod | None = Query(default=None),
    search: str | None = Query(default=None, max_length=200),
    # --- pagination / sorting ---
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    sort_by: str = Query(default="date", pattern="^(date|amount|created_at)$"),
    order: Literal["asc", "desc"] = Query(default="desc"),
    # --- deps ---
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ExpenseListResponse:
    filters = ExpenseFilters(
        category_id=category_id,
        date_from=date_from,
        date_to=date_to,
        payment_method=payment_method,
        search=search,
        page=page,
        limit=limit,
        sort_by=sort_by,
        order=order,
    )
    return await get_expenses(db, current_user.id, filters)


@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense_route(
    body: CreateExpenseRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ExpenseResponse:
    expense = await create_expense(db, current_user.id, body)
    return ExpenseResponse.model_validate(expense)


@router.get("/{expense_id}", response_model=ExpenseResponse, status_code=status.HTTP_200_OK)
async def get_expense_route(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ExpenseResponse:
    expense = await get_expense_by_id(db, current_user.id, expense_id)
    return ExpenseResponse.model_validate(expense)


@router.put("/{expense_id}", response_model=ExpenseResponse, status_code=status.HTTP_200_OK)
async def update_expense_route(
    expense_id: int,
    body: UpdateExpenseRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ExpenseResponse:
    expense = await update_expense(db, current_user.id, expense_id, body)
    return ExpenseResponse.model_validate(expense)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense_route(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    await delete_expense(db, current_user.id, expense_id)

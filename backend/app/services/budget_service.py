from datetime import date
from decimal import Decimal
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.budget import Budget
from app.models.expense import Expense
from app.schemas.budget import BudgetResponse, SetBudgetRequest


# ---------------------------------------------------------------------------
# Internal helper — compute spent + derived fields for a single budget row
# ---------------------------------------------------------------------------

async def _build_response(db: AsyncSession, budget: Budget) -> BudgetResponse:
    """Query the actual spend for this budget's period and compute all fields."""

    # Base spent query: expenses for this user in this month+year
    stmt = (
        select(func.coalesce(func.sum(Expense.amount), 0))
        .where(
            Expense.user_id == budget.user_id,
            extract("month", Expense.date) == budget.month,
            extract("year", Expense.date) == budget.year,
        )
    )

    # If category_id is set, filter to that category only;
    # if None it is an overall budget — sum all categories.
    if budget.category_id is not None:
        stmt = stmt.where(Expense.category_id == budget.category_id)

    result = await db.execute(stmt)
    spent: float = float(result.scalar_one())

    budget_amount: float = float(budget.amount)
    utilization_pct: float = (spent / budget_amount * 100) if budget_amount > 0 else 0.0

    return BudgetResponse(
        id=budget.id,
        user_id=budget.user_id,
        category_id=budget.category_id,
        amount=Decimal(str(budget.amount)),
        month=budget.month,
        year=budget.year,
        spent=spent,
        utilization_pct=round(utilization_pct, 2),
        alert_80=utilization_pct >= 80,
        alert_100=utilization_pct >= 100,
    )


# ---------------------------------------------------------------------------
# Service functions
# ---------------------------------------------------------------------------

async def get_budgets(
    db: AsyncSession,
    user_id: int,
    month: int,
    year: int,
) -> list[BudgetResponse]:
    """Return all budgets for the user in the given month+year, with computed spend."""
    stmt = (
        select(Budget)
        .where(
            Budget.user_id == user_id,
            Budget.month == month,
            Budget.year == year,
        )
        .order_by(Budget.category_id.asc().nullsfirst())
    )
    result = await db.execute(stmt)
    budgets = list(result.scalars().all())

    return [await _build_response(db, b) for b in budgets]


async def set_budget(
    db: AsyncSession,
    user_id: int,
    data: SetBudgetRequest,
) -> BudgetResponse:
    """Upsert a budget: update amount if one already exists for this
    (user_id, category_id, month, year) combination, otherwise create."""

    # Look up existing budget for this slot
    stmt = select(Budget).where(
        Budget.user_id == user_id,
        Budget.month == data.month,
        Budget.year == data.year,
    )
    # Handle NULL category_id correctly — IS NULL vs = ?
    if data.category_id is None:
        stmt = stmt.where(Budget.category_id.is_(None))
    else:
        stmt = stmt.where(Budget.category_id == data.category_id)

    result = await db.execute(stmt)
    budget = result.scalar_one_or_none()

    if budget is not None:
        # Update existing
        budget.amount = data.amount
    else:
        # Create new
        budget = Budget(
            user_id=user_id,
            category_id=data.category_id,
            amount=data.amount,
            month=data.month,
            year=data.year,
        )
        db.add(budget)

    await db.commit()
    await db.refresh(budget)
    return await _build_response(db, budget)


async def delete_budget(
    db: AsyncSession,
    user_id: int,
    budget_id: int,
) -> None:
    """Delete a budget; raises 404 if not found or not owned by the user."""
    budget = await db.get(Budget, budget_id)
    if budget is None or budget.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found.",
        )
    await db.delete(budget)
    await db.commit()
    return None

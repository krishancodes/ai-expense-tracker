from datetime import date
from decimal import Decimal
from typing import Literal, Optional

from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import Expense, PaymentMethod
from app.models.insight_cache import InsightCache
from app.schemas.expense import (
    CreateExpenseRequest,
    ExpenseFilters,
    ExpenseListResponse,
    ExpenseResponse,
    UpdateExpenseRequest,
)


# ExpenseFilters is defined in app.schemas.expense and imported above


# ---------------------------------------------------------------------------
# Cache invalidation helper
# ---------------------------------------------------------------------------

async def _invalidate_insight_cache(db: AsyncSession, user_id: int, expense_date: date) -> None:
    """Delete the insight_cache row for the user's month/year of the given expense date."""
    await db.execute(
        delete(InsightCache).where(
            InsightCache.user_id == user_id,
            InsightCache.month == expense_date.month,
            InsightCache.year == expense_date.year,
        )
    )
    # commit is handled by the caller


# ---------------------------------------------------------------------------
# Allowed sort columns (whitelist to prevent SQL injection via sort_by param)
# ---------------------------------------------------------------------------

_SORTABLE_COLUMNS: dict[str, object] = {
    "date": Expense.date,
    "amount": Expense.amount,
    "created_at": Expense.created_at,
}


# ---------------------------------------------------------------------------
# Service functions
# ---------------------------------------------------------------------------

async def get_expenses(
    db: AsyncSession,
    user_id: int,
    filters: ExpenseFilters,
) -> ExpenseListResponse:
    """Return a paginated, filtered, sorted list of expenses for the user."""

    stmt = select(Expense).where(Expense.user_id == user_id)

    # --- Optional filters ---
    if filters.category_id is not None:
        stmt = stmt.where(Expense.category_id == filters.category_id)
    if filters.date_from is not None:
        stmt = stmt.where(Expense.date >= filters.date_from)
    if filters.date_to is not None:
        stmt = stmt.where(Expense.date <= filters.date_to)
    if filters.payment_method is not None:
        stmt = stmt.where(Expense.payment_method == filters.payment_method)
    if filters.search:
        stmt = stmt.where(Expense.description.ilike(f"%{filters.search}%"))

    # --- Count total rows before pagination ---
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total: int = (await db.execute(count_stmt)).scalar_one()

    # --- Sorting ---
    sort_col = _SORTABLE_COLUMNS.get(filters.sort_by, Expense.date)
    if filters.order == "asc":
        stmt = stmt.order_by(sort_col.asc())
    else:
        stmt = stmt.order_by(sort_col.desc())

    # --- Pagination ---
    offset = (filters.page - 1) * filters.limit
    stmt = stmt.offset(offset).limit(filters.limit)

    result = await db.execute(stmt)
    expenses = list(result.scalars().all())

    return ExpenseListResponse(
        data=[ExpenseResponse.model_validate(e) for e in expenses],
        total=total,
        page=filters.page,
        limit=filters.limit,
    )


async def get_expense_by_id(
    db: AsyncSession,
    user_id: int,
    expense_id: int,
) -> Expense:
    """Return a single expense; raises 404 if not found or not owned by user."""
    expense = await db.get(Expense, expense_id)
    if expense is None or expense.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found.",
        )
    return expense


async def create_expense(
    db: AsyncSession,
    user_id: int,
    data: CreateExpenseRequest,
) -> Expense:
    """Create an expense.

    Raises 422 with code EXPENSE_FUTURE_DATE if date is in the future.
    (The schema validator also catches this — this guard is the service-layer
    canonical check in case the schema validation is bypassed or reused.)
    """
    if data.date > date.today():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "EXPENSE_FUTURE_DATE", "message": "Expense date must not be in the future."},
        )

    expense = Expense(
        user_id=user_id,
        category_id=data.category_id,
        amount=data.amount,
        date=data.date,
        description=data.description,
        payment_method=data.payment_method,
    )
    db.add(expense)

    await _invalidate_insight_cache(db, user_id, data.date)
    await db.commit()
    await db.refresh(expense)
    return expense


async def update_expense(
    db: AsyncSession,
    user_id: int,
    expense_id: int,
    data: UpdateExpenseRequest,
) -> Expense:
    """Update an expense; only writes fields that are not None in data.

    Invalidates insight_cache when date or amount changes.
    """
    expense = await get_expense_by_id(db, user_id, expense_id)

    date_changed = data.date is not None and data.date != expense.date
    amount_changed = data.amount is not None and Decimal(str(expense.amount)) != data.amount

    # Capture old date before update (needed if date itself changes)
    old_date: date = expense.date

    if data.amount is not None:
        expense.amount = data.amount
    if data.category_id is not None:
        expense.category_id = data.category_id
    if data.date is not None:
        expense.date = data.date
    if data.description is not None:
        expense.description = data.description
    if data.payment_method is not None:
        expense.payment_method = data.payment_method

    if date_changed or amount_changed:
        # Invalidate old month/year cache
        await _invalidate_insight_cache(db, user_id, old_date)
        # If the date moved to a different month, invalidate that one too
        if date_changed and data.date is not None:
            await _invalidate_insight_cache(db, user_id, data.date)

    await db.commit()
    await db.refresh(expense)
    return expense


async def delete_expense(
    db: AsyncSession,
    user_id: int,
    expense_id: int,
) -> None:
    """Delete an expense and invalidate its month's insight cache."""
    expense = await get_expense_by_id(db, user_id, expense_id)

    await _invalidate_insight_cache(db, user_id, expense.date)
    await db.delete(expense)
    await db.commit()
    return None

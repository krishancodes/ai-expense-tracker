from datetime import date
from typing import Optional

from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.budget import Budget
from app.models.category import Category
from app.models.expense import Expense
from app.schemas.dashboard import (
    CategoryBudgetStatus,
    CategorySpend,
    DashboardSummaryResponse,
    MonthlyTrend,
)


def _prev_months(month: int, year: int, n: int) -> list[tuple[int, int]]:
    """Return the last n calendar months as (month, year) tuples,
    oldest first, ending at (month, year) inclusive."""
    months = []
    m, y = month, year
    for _ in range(n):
        months.append((m, y))
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    return list(reversed(months))


async def get_dashboard_summary(
    db: AsyncSession,
    user_id: int,
    month: int,
    year: int,
) -> DashboardSummaryResponse:

    # -----------------------------------------------------------------------
    # 1. Total spent this month
    # -----------------------------------------------------------------------
    total_spent_result = await db.execute(
        select(func.coalesce(func.sum(Expense.amount), 0)).where(
            Expense.user_id == user_id,
            extract("month", Expense.date) == month,
            extract("year", Expense.date) == year,
        )
    )
    total_spent: float = float(total_spent_result.scalar_one())

    # -----------------------------------------------------------------------
    # 2. Overall budget (category_id IS NULL)
    # -----------------------------------------------------------------------
    overall_budget_result = await db.execute(
        select(Budget).where(
            Budget.user_id == user_id,
            Budget.month == month,
            Budget.year == year,
            Budget.category_id.is_(None),
        )
    )
    overall_budget_row = overall_budget_result.scalar_one_or_none()

    overall_budget: Optional[float] = None
    budget_remaining: Optional[float] = None
    utilization_pct: Optional[float] = None

    if overall_budget_row is not None:
        overall_budget = float(overall_budget_row.amount)
        budget_remaining = round(overall_budget - total_spent, 2)
        utilization_pct = round(
            (total_spent / overall_budget * 100) if overall_budget > 0 else 0.0, 2
        )

    # -----------------------------------------------------------------------
    # 3. Per-category spend this month (for top_categories + breakdown)
    # -----------------------------------------------------------------------
    cat_spend_result = await db.execute(
        select(
            Category.id,
            Category.name,
            Category.color,
            Category.icon,
            func.coalesce(func.sum(Expense.amount), 0).label("spent"),
        )
        .join(Expense, Expense.category_id == Category.id, isouter=True)
        .where(
            Expense.user_id == user_id,
            extract("month", Expense.date) == month,
            extract("year", Expense.date) == year,
        )
        .group_by(Category.id, Category.name, Category.color, Category.icon)
        .order_by(func.sum(Expense.amount).desc())
    )
    cat_rows = cat_spend_result.all()  # list of (id, name, color, icon, spent)

    # -----------------------------------------------------------------------
    # 4. Top 3 categories by spend
    # -----------------------------------------------------------------------
    top_categories: list[CategorySpend] = []
    for row in cat_rows[:3]:
        _id, name, color, icon, spent = row
        spent_f = float(spent)
        pct = round((spent_f / total_spent * 100) if total_spent > 0 else 0.0, 2)
        top_categories.append(
            CategorySpend(name=name, spent=spent_f, pct=pct, color=color, icon=icon)
        )

    # -----------------------------------------------------------------------
    # 5. Monthly trend — last 6 months incl. current
    # -----------------------------------------------------------------------
    trend_periods = _prev_months(month, year, 6)

    # Fetch all in one query: group by MONTH + YEAR
    trend_result = await db.execute(
        select(
            extract("month", Expense.date).label("m"),
            extract("year", Expense.date).label("y"),
            func.coalesce(func.sum(Expense.amount), 0).label("total"),
        )
        .where(Expense.user_id == user_id)
        .group_by("m", "y")
    )
    # Build a lookup dict from DB results
    trend_lookup: dict[tuple[int, int], float] = {
        (int(row.m), int(row.y)): float(row.total)
        for row in trend_result.all()
    }

    monthly_trend: list[MonthlyTrend] = [
        MonthlyTrend(month=m, year=y, total=trend_lookup.get((m, y), 0.0))
        for m, y in trend_periods
    ]

    # -----------------------------------------------------------------------
    # 6. Category breakdown — categories with expenses OR a budget this month
    # -----------------------------------------------------------------------

    # Fetch per-category budgets for this month
    budget_result = await db.execute(
        select(Budget).where(
            Budget.user_id == user_id,
            Budget.month == month,
            Budget.year == year,
            Budget.category_id.isnot(None),  # exclude overall budget row
        )
    )
    budget_rows = budget_result.scalars().all()
    budgets_by_cat: dict[int, float] = {
        b.category_id: float(b.amount) for b in budget_rows
    }

    # Build spend lookup from cat_rows
    spend_by_cat: dict[int, tuple[str, float]] = {
        row[0]: (row[1], float(row[4])) for row in cat_rows  # id → (name, spent)
    }

    # Union of category IDs that appear in either set
    all_cat_ids = set(spend_by_cat.keys()) | set(budgets_by_cat.keys())

    # Resolve names for any budget-only categories (no spend → not in cat_rows)
    missing_ids = all_cat_ids - set(spend_by_cat.keys())
    if missing_ids:
        name_result = await db.execute(
            select(Category.id, Category.name).where(Category.id.in_(missing_ids))
        )
        for row in name_result.all():
            spend_by_cat[row.id] = (row.name, 0.0)

    category_breakdown: list[CategoryBudgetStatus] = []
    for cat_id in sorted(all_cat_ids):
        cat_name, spent_val = spend_by_cat.get(cat_id, ("Unknown", 0.0))
        budget_val = budgets_by_cat.get(cat_id)
        util = (
            round(spent_val / budget_val * 100, 2)
            if budget_val and budget_val > 0
            else None
        )
        category_breakdown.append(
            CategoryBudgetStatus(
                category=cat_name,
                spent=spent_val,
                budget=budget_val,
                utilization_pct=util,
            )
        )

    return DashboardSummaryResponse(
        total_spent=round(total_spent, 2),
        overall_budget=overall_budget,
        budget_remaining=budget_remaining,
        utilization_pct=utilization_pct,
        top_categories=top_categories,
        monthly_trend=monthly_trend,
        category_breakdown=category_breakdown,
    )

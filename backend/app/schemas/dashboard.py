from typing import Optional

from pydantic import BaseModel


class CategorySpend(BaseModel):
    name: str
    spent: float
    pct: float          # percentage of total_spent this month
    color: Optional[str]
    icon: Optional[str]


class MonthlyTrend(BaseModel):
    month: int
    year: int
    total: float


class CategoryBudgetStatus(BaseModel):
    category: str           # category name (or "Overall" for null category_id)
    spent: float
    budget: Optional[float] # None if no budget set for this category this month
    utilization_pct: Optional[float]


class DashboardSummaryResponse(BaseModel):
    total_spent: float
    overall_budget: Optional[float]      # None if no overall budget set
    budget_remaining: Optional[float]    # None if no overall budget set
    utilization_pct: Optional[float]     # None if no overall budget set
    top_categories: list[CategorySpend]  # top 3 by spend this month
    monthly_trend: list[MonthlyTrend]    # last 6 calendar months incl. current
    category_breakdown: list[CategoryBudgetStatus]

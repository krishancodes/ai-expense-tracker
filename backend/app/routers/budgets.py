from datetime import date

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.budget import BudgetResponse, SetBudgetRequest
from app.services.budget_service import delete_budget, get_budgets, set_budget

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.get("", response_model=list[BudgetResponse], status_code=status.HTTP_200_OK)
async def list_budgets(
    month: int = date.today().month,
    year: int = date.today().year,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[BudgetResponse]:
    return await get_budgets(db, current_user.id, month, year)


@router.post("", response_model=BudgetResponse, status_code=status.HTTP_200_OK)
async def upsert_budget(
    body: SetBudgetRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BudgetResponse:
    return await set_budget(db, current_user.id, body)


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_budget(
    budget_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    await delete_budget(db, current_user.id, budget_id)

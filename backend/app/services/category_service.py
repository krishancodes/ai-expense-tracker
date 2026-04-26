from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.expense import Expense
from app.schemas.category import CreateCategoryRequest, UpdateCategoryRequest


async def get_all_categories(db: AsyncSession, user_id: int) -> list[Category]:
    """Return system categories (user_id IS NULL) + the user's own categories,
    ordered by is_system DESC, name ASC."""
    stmt = (
        select(Category)
        .where(
            or_(Category.user_id.is_(None), Category.user_id == user_id)
        )
        .order_by(Category.is_system.desc(), Category.name.asc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_category(
    db: AsyncSession, user_id: int, data: CreateCategoryRequest
) -> Category:
    """Create a custom category for the user.
    Raises 400 if the user already has 20 or more custom categories."""
    count_stmt = (
        select(func.count())
        .select_from(Category)
        .where(Category.user_id == user_id)
    )
    count_result = await db.execute(count_stmt)
    custom_count = count_result.scalar_one()

    if custom_count >= 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Custom category limit reached (maximum 20).",
        )

    category = Category(
        user_id=user_id,
        name=data.name,
        icon=data.icon,
        color=data.color,
        is_system=False,
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def update_category(
    db: AsyncSession,
    user_id: int,
    category_id: int,
    data: UpdateCategoryRequest,
) -> Category:
    """Update a user-owned category.

    Raises:
        404 – category not found
        403 (CATEGORY_SYSTEM_READONLY) – attempt to edit a system category
        403 – category belongs to a different user
    """
    category = await db.get(Category, category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found.",
        )

    if category.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "CATEGORY_SYSTEM_READONLY", "message": "System categories cannot be modified."},
        )

    if category.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this category.",
        )

    if data.name is not None:
        category.name = data.name
    if data.icon is not None:
        category.icon = data.icon
    if data.color is not None:
        category.color = data.color

    await db.commit()
    await db.refresh(category)
    return category


async def delete_category(
    db: AsyncSession, user_id: int, category_id: int
) -> None:
    """Delete a user-owned category.

    Raises:
        404 – category not found
        403 (CATEGORY_SYSTEM_READONLY) – attempt to delete a system category
        403 – category belongs to a different user
        409 (CATEGORY_HAS_EXPENSES) – expenses still reference this category
    """
    category = await db.get(Category, category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found.",
        )

    if category.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "CATEGORY_SYSTEM_READONLY", "message": "System categories cannot be deleted."},
        )

    if category.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this category.",
        )

    expense_count_stmt = (
        select(func.count())
        .select_from(Expense)
        .where(Expense.category_id == category_id)
    )
    expense_count_result = await db.execute(expense_count_stmt)
    expense_count = expense_count_result.scalar_one()

    if expense_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "CATEGORY_HAS_EXPENSES", "message": "Cannot delete a category that has associated expenses."},
        )

    await db.delete(category)
    await db.commit()
    return None

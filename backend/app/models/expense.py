from __future__ import annotations

import enum
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.user import User


class PaymentMethod(str, enum.Enum):
    Cash = "Cash"
    UPI = "UPI"
    Card = "Card"
    NetBanking = "NetBanking"


class Expense(Base):
    __tablename__ = "expenses"
    __table_args__ = (
    Index("ix_expenses_user_date", "user_id", "date"),
    CheckConstraint("amount > 0", name="ck_expenses_amount_positive"),
)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE")
    )
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id")
    )
    amount: Mapped[float] = mapped_column(Numeric(10, 2))
    date: Mapped[date] = mapped_column(Date)
    description: Mapped[str | None] = mapped_column(String(200), nullable=True)
    payment_method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod, name="paymentmethod")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    user: Mapped[User] = relationship("User", back_populates="expenses")
    category: Mapped[Category] = relationship("Category", back_populates="expenses")

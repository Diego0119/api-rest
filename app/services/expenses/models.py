from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.services.accounts.models import User


class Expense(Base):
    __tablename__ = "expenses_expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(64))
    description: Mapped[Optional[str]]
    datetime: Mapped[Optional[datetime]]
    amount: Mapped[int]
    created_by_id: Mapped[int] = mapped_column(ForeignKey("accounts_users.id"))

    created_by: Mapped["User"] = relationship(back_populates="created_expenses")
    debts: Mapped[list["Debt"]] = relationship(back_populates="expense", cascade="all, delete")

    def __repr__(self) -> str:
        return f"<Expense(title={self.title})>"


class Debt(Base):
    __tablename__ = "expenses_debts"

    expense_id: Mapped[int] = mapped_column(ForeignKey("expenses_expenses.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("accounts_users.id"), primary_key=True)
    amount: Mapped[int]
    paid_on: Mapped[Optional[datetime]]

    expense: Mapped["Expense"] = relationship(back_populates="debts")
    user: Mapped["User"] = relationship(back_populates="debts")

    def __repr__(self) -> str:
        return f"<Debt(expense_id={self.expense_id}, user_id={self.user_id}, amount={self.amount})>"

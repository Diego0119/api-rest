from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.services.expenses.models import Debt, Expense


class User(Base):
    __tablename__ = "accounts_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    full_name: Mapped[str]
    email: Mapped[Optional[str]] = mapped_column(unique=True, index=True)
    password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)

    created_expenses: Mapped[list["Expense"]] = relationship(back_populates="created_by")
    debts: Mapped[list["Debt"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"<User(username={self.username})>"

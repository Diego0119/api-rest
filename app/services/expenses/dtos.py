from advanced_alchemy.extensions.litestar import SQLAlchemyDTO
from litestar.dto import DTOConfig

from .models import Debt, Expense


class ExpenseDTO(SQLAlchemyDTO[Expense]):
    config = DTOConfig(exclude={"created_by.password"})


class ExpenseCreateDTO(SQLAlchemyDTO[Expense]):
    config = DTOConfig(
        exclude={"id", "created_by_id", "created_by", "debts.0.expense_id", "debts.0.amount", "debts.0.paid_on"}
    )


class ExpenseUpdateDTO(SQLAlchemyDTO[Expense]):
    config = DTOConfig(exclude={"id", "created_by"}, partial=True)


class DebtDTO(SQLAlchemyDTO[Debt]):
    pass


class DebtCreateDTO(SQLAlchemyDTO[Debt]):
    config = DTOConfig(exclude={"id"})


class DebtUpdateDTO(SQLAlchemyDTO[Debt]):
    config = DTOConfig(exclude={"id"}, partial=True)

from advanced_alchemy.extensions.litestar import SQLAlchemyDTO, SQLAlchemyDTOConfig

from .models import Debt, Expense


class ExpenseDTO(SQLAlchemyDTO[Expense]):
    config = SQLAlchemyDTOConfig(exclude={"created_by.password"})


class ExpenseCreateDTO(SQLAlchemyDTO[Expense]):
    config = SQLAlchemyDTOConfig(include={"title", "description", "datetime", "amount", "debts.0.user_id"})


class ExpenseUpdateDTO(SQLAlchemyDTO[Expense]):
    config = SQLAlchemyDTOConfig(exclude={"id", "created_by"}, partial=True)


class DebtDTO(SQLAlchemyDTO[Debt]):
    pass


class DebtCreateDTO(SQLAlchemyDTO[Debt]):
    config = SQLAlchemyDTOConfig(exclude={"id"})


class DebtUpdateDTO(SQLAlchemyDTO[Debt]):
    config = SQLAlchemyDTOConfig(exclude={"id"}, partial=True)

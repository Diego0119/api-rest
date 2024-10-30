from datetime import datetime

from advanced_alchemy.repository import SQLAlchemySyncRepository
from sqlalchemy.orm import Session

from app.services.accounts.models import User

from .models import Debt, Expense


class ExpenseRepository(SQLAlchemySyncRepository[Expense]):
    model_type = Expense

    def create_with_debts(self, expense: Expense, created_by: User) -> Expense:
        """"""
        # exclude the user who created the expense from the debts (if it is included)
        debts = [d for d in expense.debts if d.user_id != created_by.id]
        # calculate the amount per person
        amount_per_person = int(expense.amount / (len(debts) + 1))
        # create debts for each user
        expense.debts = [Debt(amount=amount_per_person, user_id=d.user_id) for d in debts]
        expense.created_by = created_by
        # if datetime is not provided, set it to the current time
        if not expense.datetime:
            expense.datetime = datetime.now()

        return self.add(expense)


class DebtRepository(SQLAlchemySyncRepository[Debt]):
    model_type = Debt


async def provide_expense_repository(db_session: Session) -> ExpenseRepository:
    return ExpenseRepository(session=db_session)


async def provide_debt_repository(db_session: Session) -> DebtRepository:
    return DebtRepository(session=db_session)

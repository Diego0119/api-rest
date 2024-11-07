from typing import Any

from advanced_alchemy.exceptions import NotFoundError
from litestar import Controller, Request, Router, delete, get, patch, post
from litestar.di import Provide
from litestar.dto import DTOData
from litestar.exceptions import HTTPException
from litestar.security.jwt import Token

from app.services.accounts.models import User

from .dtos import ExpenseCreateDTO, ExpenseDTO, ExpenseUpdateDTO, ExpensesDTO
from .models import Expense
from .repositories import ExpenseRepository, provide_expense_repository


class ExpenseController(Controller):
    """Controller for expense management."""

    path = "/expenses"
    tags = ["expenses | expenses"]
    return_dto = ExpenseDTO
    dependencies = {"expenses_repo": Provide(provide_expense_repository)}

    @get(return_dto=ExpensesDTO)
    async def list_expenses(self, expenses_repo: ExpenseRepository) -> list[Expense]:
        return expenses_repo.list()

    @post(dto=ExpenseCreateDTO)
    async def create_expense(
        self, request: "Request[User, Token, Any]", expenses_repo: ExpenseRepository, data: Expense
    ) -> Expense:
        if not request.user:
            raise HTTPException(detail="Usuario no autenticado", status_code=401)
        return expenses_repo.create_with_debts(data, request.user)

    @get("/{expense_id:int}")
    async def get_expense(self, expenses_repo: ExpenseRepository, expense_id: int) -> Expense:
        try:
            return expenses_repo.get(expense_id)
        except NotFoundError:
            raise HTTPException(detail="Expense not found", status_code=404)

    @patch("/{expense_id:int}", dto=ExpenseUpdateDTO)
    async def update_expense(
        self,expenses_repo: ExpenseRepository, expense_id: int, data: DTOData[Expense]
    ) -> Expense:
        try:
            expense, _ = expenses_repo.get_and_update(id=expense_id, **data.as_builtins(), match_fields=["id"])
            return expense
        except NotFoundError:
            raise HTTPException(detail="User not found", status_code=404)

    @delete("/{expense_id:int}")
    async def delete_expense(self, expenses_repo: ExpenseRepository, expense_id: int) -> None:
        try:
            expenses_repo.soft_delete(expense_id)
        except NotFoundException:
            raise HTTPException(status_code=404, detail="Gasto no encontrado.")

    @post("/{id:int}/pay")
    async def pay_expense(self,id:int, request: "Request[User, Token, Any]",expenses_repo: ExpenseRepository,) -> str:
        if not request.user:
            raise HTTPException(detail="Usuario no autenticado", status_code=401)

        user_id = request.user.id
        result = expenses_repo.update_expense(id,user_id)
        return result


expenses_router = Router(
    route_handlers=[ExpenseController],
    path="/expenses",
)

from datetime import datetime

from advanced_alchemy.repository import SQLAlchemySyncRepository
from sqlalchemy.orm import Session
import jwt
from app.services.accounts.models import User
from litestar import Controller, Request, Response
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

    def get_one(self, id: int) -> Expense:
        """Obtiene un gasto por su ID."""
        return self.session.query(Expense).filter_by(id=id).first()

    def list(self) -> list[Expense]:
        return self.session.query(Expense).filter(Expense.is_deleted == False).all()

    def get_expense_by_id(self, expense_id) -> Expense:
        return self.session.query(Expense).filter(Expense.id == expense_id).one_or_none()

    def update(self, expense: Expense) -> None:
        self.session.add(expense) 
        self.session.commit()  

    def update_expense(self, expense_id: int, user_id: int):
        """Realiza el pago de un gasto si tiene deudas asociadas para el usuario especificado."""
        expense = self.get_expense_by_id(expense_id)

        if not expense:
            raise NotFoundException("Gasto no encontrado.")

        debts = expense.debts

        if not debts:
            raise HTTPException(detail="No hay deudas asociadas a este gasto.", status_code=400)

        all_debts_paid = True  # Variable para verificar si todas las deudas han sido pagadas

        for debt in debts:
            if debt.user_id == user_id:  # Solo procesar la deuda del usuario específico
                if debt.paid_on is None:  # Si la deuda no ha sido pagada
                    debt.paid_on = datetime.now()  # Establecer la fecha de pago
                    debt.amount = 0  # Marcar la deuda como pagada
                else:
                    all_debts_paid = False  # Hay al menos una deuda que no ha sido pagada

                self.session.add(debt)  # Añadir la deuda a la sesión para actualizarla

        # Actualizar el estado del gasto según el estado de las deudas
        expense.update_status()
        self.session.add(expense)  # Añadir el gasto a la sesión para actualizarlo

        self.session.commit()  # Confirmar cambios en la base de datos

        return Response(
            content={"message": "Deuda(s) pagada(s) correctamente"},
            status_code=200,
            media_type="application/json"
        )
    def retrieve_user_from_token(self, token: str) -> User:

        try:
            payload = jwt.decode(token, "secret", algorithms=["HS256"])
        except jwt.exceptions.DecodeError:
            raise IndentationError("Token inválido o con padding incorrecto.")
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token expirado.")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Token inválido.")

            user_id = payload.get("sub")

        if not user_id:
            raise AuthenticationError("Token inválido o usuario no encontrado.")
        
            user = self.get_user_by_id(user_id)
        if not user:
            raise AuthenticationError("Usuario no encontrado.")
        
        return user

    def soft_delete(self, expense_id: int) -> Response:
        """Marca el gasto como eliminado en lugar de eliminarlo físicamente."""
        expense = self.get_expense_by_id(expense_id)
        if not expense:
            return Response(
            content={"message": "Gasto no encontrado"},
            status_code=204,
            media_type="application/json"
        )

        expense.is_deleted = True
        self.session.add(expense)
        self.session.commit()
        return Response(
            content={"message": "Gasto borrado correctamente"},
            status_code=200,
            media_type="application/json"
        )


class DebtRepository(SQLAlchemySyncRepository[Debt]):
    model_type = Debt


async def provide_expense_repository(db_session: Session) -> ExpenseRepository:
    return ExpenseRepository(session=db_session)


async def provide_debt_repository(db_session: Session) -> DebtRepository:
    return DebtRepository(session=db_session)

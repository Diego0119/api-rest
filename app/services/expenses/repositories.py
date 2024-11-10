from datetime import datetime
from typing import Optional, Any, overload
from advanced_alchemy.repository import SQLAlchemySyncRepository
from sqlalchemy.orm import Session
import jwt
from app.services.accounts.models import User
from litestar import Controller, Request, Response
from .models import Debt, Expense
from sqlalchemy.orm import aliased
from litestar.exceptions import HTTPException


class ExpenseRepository(SQLAlchemySyncRepository[Expense]):
    model_type = Expense

    def create_with_debts(self, expense: Expense, created_by: User) -> Expense:
        """"""
        debts = [d for d in expense.debts if d.user_id != created_by.id]
        # calculate the amount per person
        amount_per_person = int(expense.amount / (len(debts) + 1))
        # create debts for each user
        expense.debts = [Debt(amount=amount_per_person, user_id=d.user_id) for d in debts]
        expense.created_by = created_by
        if not expense.datetime:
            expense.datetime = datetime.now()

        return self.add(expense)

    def get_one(self, id: int) -> Optional[Expense]:  # type: ignore[override]
        """Obtiene un gasto por su ID."""
        return self.session.query(Expense).filter_by(id=id).first()

    def list(self) -> list[Expense]: # type: ignore[override]
        return self.session.query(Expense).filter(Expense.is_deleted == False).all()

    def get_expense_by_id(self, expense_id:int) -> Optional[Expense]:
        return self.session.query(Expense).filter(Expense.id == expense_id).one_or_none()

    def update(self, expense: Expense) -> None: # type: ignore[override]
        self.session.add(expense) 
        self.session.commit()  

    def update_expense(self, expense_id: int, user_id: int) ->Response[Any]:
        """Realiza el pago de un gasto si tiene deudas asociadas para el usuario especificado."""
        expense = self.get_expense_by_id(expense_id)

        if not expense:
            raise HTTPException(detail="Gasto no encontrado", status_code=404)

        debts = expense.debts

        if not debts:
            raise HTTPException(detail="No hay deudas asociadas a este gasto.", status_code=400)

        all_debts_paid = True 

        for debt in debts:
            if debt.user_id != user_id:
                return Response(
                content={"message": "La deuda no es suya, solo la puede pagar el usuario que carga con ella."},
                status_code=403,
                media_type="application/json"
                )
                
            if debt.user_id == user_id: 
                if debt.paid_on is None:  
                    debt.paid_on = datetime.now()  
                    debt.amount = 0  
                else:
                    all_debts_paid = False  

                self.session.add(debt)  

        expense.update_status()
        self.session.add(expense)  

        self.session.commit()  

        return Response(
            content={"message": "Deuda(s) pagada(s) correctamente"},
            status_code=200,
            media_type="application/json"
        )
    def retrieve_user_from_token(self, token: str) -> User:

        try:
            payload = jwt.decode(token, "secret", algorithms=["HS256"])
        except jwt.exceptions.DecodeError:
            raise HTTPException(detail="Token invalido o incorrecto.", status_code=403)
        except jwt.ExpiredSignatureError:
            raise HTTPException(detail="Token expirado.", status_code=403)
        except jwt.InvalidTokenError:
            raise HTTPException(detail="Token invalido.", status_code=403)

            user_id: int = payload.get("sub")

        if not user_id:
            raise HTTPException(detail="Token invalido o usuario no encontrado.", status_code=403)
        
            user: User = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(detail="Usuario no encontrado.", status_code=404)
        
        return user

    def soft_delete(self, expense_id: int) -> Response[Any]:
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

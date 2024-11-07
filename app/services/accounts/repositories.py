from advanced_alchemy.repository import SQLAlchemySyncRepository
from pwdlib import PasswordHash
from sqlalchemy.orm import Session
import jwt
from datetime import datetime, timedelta 
from typing import Optional
from sqlalchemy import select,null
import sqlalchemy as sa
from datetime import datetime 
from .models import User
from app.services.expenses.models import Debt
from app.services.expenses.models import Expense
from litestar import Controller, Request, Response

password_hasher = PasswordHash.recommended()


class UserRepository(SQLAlchemySyncRepository[User]):
    model_type = User

    def add_with_password_hash(self, user: User) -> User:
        """Creates a new user hashing the password."""
        password_hasher.hash(user.password)
        return self.add(user)

    def update_last_login(self, user: User) -> None:
        """Updates the last_login field of an existing user."""
        user.last_login = datetime.utcnow()  
        self.update(user) 
        self.session.commit() 

    def update_password(self, user: User, new_password: str) -> None:
        """Hashes and updates the user's password."""
        user.password = new_password
        self.update(user)
        self.session.commit()

    def get_one_or_none(self, username: str) -> User:
        """Retrieve one user by username or return None if not found."""
        user = self.session.query(User).filter(User.username == username).first()
        return user 

    def get_user_by_id(self, user_id: int) -> User:
        user = self.session.query(User).filter(User.id == user_id).one_or_none()
        if not user:
            raise NotFoundError(f"User with id {user_id} not found")
        return user


    def retrieve_user_from_token(self, token: str) -> User:
        payload = jwt.decode(token, "secret", algorithms=["HS256"])

        user_id = payload.get("user_id")

        if not user_id:
            raise AuthenticationError("Token inválido o usuario no encontrado.")
        user = self.get_user_by_id(user_id)
        if not user:
            raise AuthenticationError("Usuario no encontrado.")
        
        return user

    def create_token(self,user):
        secret_key = "secret"
        expiration_time = datetime.utcnow() + timedelta(minutes=180)
        payload = {
            'user_id': user.id,
            'name': user.full_name,
            'email': user.email,
            "iat": datetime.utcnow(),
            'exp': expiration_time,
            'sub': str(user.username),
            'is_active': user.is_active
        }
        token = jwt.encode(payload, secret_key, algorithm='HS256')

        expiration_minutes = (expiration_time - datetime.utcnow()).total_seconds() // 60
        return token, expiration_minutes

    def delete_user(self, user_id: int) -> None:
        user = self.session.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(detail="Usuario no encontrado", status_code=404)
        
        user.is_active = False
        self.session.add(user) 
        self.session.commit() 
        return Response(
                content={"message": "El usuario ha sido desactivado con exito"},
                status_code=200,
                media_type="application/json"
                )

    def get_user_expenses(self, user_id: int, status: Optional[str] = None):
        query = self.session.query(Expense).filter(Expense.created_by_id == user_id)
        
        if status:
            query = query.filter(Expense.status == status)
        else:
            query = query.filter(Expense.status != 'PAID')

        return query.all() 

    def get_user_debts(self, user_id: int):
        debts = self.session.query(Debt).filter(
            Debt.user_id == user_id,
            Debt.paid_on.is_(null())
        ).all()
        # ME FALTA PODER FILTRAR EN LOS QUE EN PAID_ON SEA NULL, LO OTRO DEL PUNTO 6 ESTA BIEN.

        return debts


    def get_user_all_debts(self, user_id: int):
        debts = self.session.query(Debt).filter(Debt.user_id == user_id).all()
        return debts


async def provide_user_repository(db_session: Session) -> UserRepository:
    return UserRepository(session=db_session)

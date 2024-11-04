from advanced_alchemy.repository import SQLAlchemySyncRepository
from pwdlib import PasswordHash
from sqlalchemy.orm import Session
import jwt
from datetime import datetime, timedelta 

from datetime import datetime 
from .models import User

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

    def get_user_by_id(self, user_id):
        return self.session.query(User).filter(User.id == user_id).one_or_none()

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
        expiration_time = datetime.utcnow() + timedelta(minutes=30)
        payload = {
            'user_id': user.id,
            'name': user.full_name,
            'email': user.email,
            'exp': expiration_time 
        }
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return token

async def provide_user_repository(db_session: Session) -> UserRepository:
    return UserRepository(session=db_session)

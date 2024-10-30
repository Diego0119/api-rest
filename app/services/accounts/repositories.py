from advanced_alchemy.repository import SQLAlchemySyncRepository
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

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
        self.session.commit() 


async def provide_user_repository(db_session: Session) -> UserRepository:
    return UserRepository(session=db_session)

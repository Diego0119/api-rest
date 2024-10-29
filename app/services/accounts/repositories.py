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


async def provide_user_repository(db_session: Session) -> UserRepository:
    return UserRepository(session=db_session)

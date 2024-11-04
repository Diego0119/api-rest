from typing import Any

from advanced_alchemy.exceptions import NotFoundError
from litestar.connection import ASGIConnection
from litestar.exceptions import NotFoundException
from litestar.security.jwt import OAuth2PasswordBearerAuth, Token

from app.config import settings
from app.database import sqlalchemy_config

from .models import User
from .repositories import UserRepository


async def retrieve_user_handler(
    token: "Token",
    _: "ASGIConnection[Any, Any, Any, Any]",
) -> User:
    """Retrieve user from the database using the token."""
    session_maker = sqlalchemy_config.create_session_maker()
    try:
        with session_maker() as session:
            return UserRepository(session=session).get_one(username=token.sub)
    except NotFoundError as e:
        raise NotFoundException("User not found") from e

# async def get_current_user(token: Token, _: ASGIConnection[Any, Any, Any, Any]) -> User:
#     """Obtener el usuario actual utilizando el token JWT."""
#     session_maker = sqlalchemy_config.create_session_maker()
#     try:
#         with session_maker() as session:
#             user = UserRepository(session=session).get_one(username=token.sub)
#             if not user:
#                 raise HTTPException(detail="Usuario no encontrado", status_code=404)
#             return user
#     except Exception as e:
#         raise HTTPEx

oauth2_auth = OAuth2PasswordBearerAuth[User](
    retrieve_user_handler=retrieve_user_handler,
    token_secret=settings.secret_key.get_secret_value(),
    token_url="/accounts/auth/login",
    exclude=["/accounts/auth", "/schema","/accounts/auth/login", "/accounts/users"],
)

from dataclasses import dataclass

from advanced_alchemy.extensions.litestar import SQLAlchemyDTO, SQLAlchemyDTOConfig
from litestar.dto import DataclassDTO

from .models import User


class UserDTO(SQLAlchemyDTO[User]):
    config = SQLAlchemyDTOConfig(exclude={"password"}, max_nested_depth=0)


class UserFullDTO(SQLAlchemyDTO[User]):
    config = SQLAlchemyDTOConfig(exclude={"password"})


class UserCreateDTO(SQLAlchemyDTO[User]):
    config = SQLAlchemyDTOConfig(exclude={"id", "is_active"}, max_nested_depth=0)


class UserUpdateDTO(SQLAlchemyDTO[User]):
    config = SQLAlchemyDTOConfig(exclude={"id", "password"}, partial=True)


@dataclass
class Login:
    username: str
    password: str


class LoginDTO(DataclassDTO[Login]):
    pass

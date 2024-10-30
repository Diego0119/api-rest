from typing import Annotated, Any

from advanced_alchemy.exceptions import IntegrityError, NotFoundError
from litestar import Controller, Request, Response, Router, delete, get, patch, post
from litestar.di import Provide
from litestar.dto import DTOData
from litestar.enums import RequestEncodingType
from litestar.exceptions import HTTPException
from litestar.params import Body
from litestar.security.jwt import Token
from litestar.status_codes import HTTP_200_OK

from .dtos import Login, LoginDTO, UserCreateDTO, UserDTO, UserFullDTO, UserUpdateDTO
from .models import User
from .repositories import UserRepository, password_hasher, provide_user_repository
from .security import oauth2_auth


class UserController(Controller):
    """Controller for user management."""

    path = "/users"
    tags = ["accounts | users"]
    return_dto = UserDTO
    dependencies = {"users_repo": Provide(provide_user_repository)}

    @get()
    async def list_users(self, users_repo: UserRepository) -> list[User]:
        return users_repo.list()

    @post(dto=UserCreateDTO)
    async def create_user(self, users_repo: UserRepository, data: User) -> User:
        try:
            return users_repo.add_with_password_hash(data)
        except IntegrityError:
            raise HTTPException(detail="Username and/or email already in use", status_code=400)

    @get("/me", return_dto=UserFullDTO)
    async def get_my_user(self, request: "Request[User, Token, Any]", users_repo: UserRepository) -> User:
        # request.user does not have a session attached, so we need to fetch the user from the database
        return users_repo.get(request.user.id)

    @get("/{user_id:int}", return_dto=UserFullDTO)
    async def get_user(self, user_id: int, users_repo: UserRepository) -> User:
        try:
            return users_repo.get(user_id)
        except NotFoundError:
            raise HTTPException(detail="User not found", status_code=404)

    @patch("/{user_id:int}", dto=UserUpdateDTO)
    async def update_user(self, user_id: int, data: DTOData[User], users_repo: UserRepository) -> User:
        try:
            user, _ = users_repo.get_and_update(id=user_id, **data.as_builtins(), match_fields=["id"])
            return user
        except NotFoundError:
            raise HTTPException(detail="User not found", status_code=404)

    @delete("/{user_id:int}")
    async def delete_user(self, user_id: int, users_repo: UserRepository) -> None:
        try:
            users_repo.delete(user_id)
        except NotFoundError:
            raise HTTPException(detail="User not found", status_code=404)


class AuthController(Controller):
    """Controller for authentication (login and logout)."""

    path = "/auth"
    tags = ["accounts | auth"]

    @post(
        "/login",
        dto=LoginDTO,
        dependencies={"users_repo": Provide(provide_user_repository)},
    )
    async def login(
        self,
        data: Annotated[Login, Body(media_type=RequestEncodingType.URL_ENCODED)],
        users_repo: UserRepository,
    ) -> Response[Any]:
        user = users_repo.get_one_or_none(username=data.username)
        if not user or not password_hasher.verify(data.password, user.password):
            raise HTTPException(detail="Invalid username or password", status_code=401)

        return oauth2_auth.login(
            identifier=str(user.username),
            response_status_code=HTTP_200_OK,
            token_extras={"name": user.full_name, "email": user.email or ""},
        )

    @post("/logout")
    async def logout(self) -> Response[None]:
        response = Response(content=None, status_code=HTTP_200_OK)
        response.delete_cookie("token")

        return response


accounts_router = Router(
    route_handlers=[UserController, AuthController],
    path="/accounts",
)

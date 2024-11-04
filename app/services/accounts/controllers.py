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
from pydantic import BaseModel
from .dtos import Login, LoginDTO, UserCreateDTO, UserDTO, UserFullDTO, UserUpdateDTO, ChangePasswordDTO
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

    class ChangePasswordRequest(BaseModel):
        current_password: str
        new_password: str

    @post("/me/change-password", return_dto=UserFullDTO)
    async def change_password(
        self,
        request: "Request[User, Token, Any]",
        users_repo: UserRepository, 
        data: ChangePasswordRequest,
    ) -> UserFullDTO:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(detail="Token de autenticación faltante o inválido", status_code=401)
        token = auth_header.split(" ")[1]

        user = users_repo.retrieve_user_from_token(token)

        # Verificar la contraseña actua
        if data.current_password != user.password:
            raise HTTPException(detail="Contraseña actual incorrecta", status_code=401)

        # Verificacion de las ultimas 3 contraseñas
        # if data.new_password in user.last_passwords[-3:]:
        #     raise HTTPException(detail="La nueva contraseña no puede ser igual a las últimas 3 contraseñas utilizadas", status_code=400)

        # Validar la nueva contraseña
        if len(data.new_password) < 8:
            raise HTTPException(detail="La nueva contraseña debe tener al menos 8 caracteres", status_code=400)

        # Hash de la nueva contraseña
        # hashed_new_password = password_hasher.hash(data.new_password)
        try:
            # users_repo.update_password(user, hashed_new_password)
            users_repo.update_password(user, data.new_password)

            # Actualizar la lista de contraseñas
            # user.last_passwords.append(user.password)  # Agregar la antigua contraseña a la lista
            # if len(user.last_passwords) > 3:
            #     user.last_passwords.pop(0)  # Mantener solo las últimas 3 contraseñas

            users_repo.update(user)
            user_data = {
                "message": "Contraseña actualizada correctamente",
                "user_info":{
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "email": user.email,
                }
            }
            return user_data 
        except IntegrityError:
            raise HTTPException(detail="Error al actualizar la contraseña", status_code=500)


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
    ) -> Response:
            user = users_repo.get_one_or_none(username=data.username)

            if not user or not data.password == user.password:
                raise HTTPException(detail="Invalid username or password", status_code=401)

            users_repo.update_last_login(user)
            
            token, expiration_minutes = users_repo.create_token(user)

            user_data = {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "email": user.email,
            }

            return Response(
                content={
                "access_token": token,
                "expires_at": f"{expiration_minutes} minutes",
                "user": user_data
            },
                status_code=200,
                media_type="application/json"
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

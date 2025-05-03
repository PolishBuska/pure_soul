from dataclasses import dataclass

from src.application.common.interactor import Interactor

from .common.id_provider import Token
from .common.password_hasher import PasswordHasher
from .common.token_generator import TokenGenerator
from .common.user_gateway import UserGateway
from ..domain.iam.exceptions import NotAuthorizedException


@dataclass
class LoginUserDTO:
    username: str
    password: str

class LoginUser(Interactor[LoginUserDTO, Token]):
    def __init__(
            self,
            user_gateway: UserGateway,
            password_hasher: PasswordHasher,
            token_generator: TokenGenerator,
    ):
        self.user_gateway = user_gateway
        self.password_hasher = password_hasher
        self.token_generator = token_generator

    async def __call__(self, dto: LoginUserDTO):
        user = await self.user_gateway.get_user_by_email(
            dto.username
        )
        if user is None:
            raise NotAuthorizedException(
                "Invalid credentials"
            )
        if not self.password_hasher.verify_password(
            hashed_password=user.password,
            password=dto.password,
        ):
            raise NotAuthorizedException('Invalid credentials')
        token_data = self.token_generator.generate_tokens(
            user
        )
        return token_data

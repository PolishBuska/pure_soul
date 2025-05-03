from dataclasses import dataclass

from src.domain.iam.user import UserService, UserId

from .common.interactor import Interactor
from .common.password_hasher import PasswordHasher
from .common.transaction_manager import TransactionManager
from .common.user_gateway import UserGateway


@dataclass
class CreateUserDTO:
    username: str
    email: str
    password: str
    age: int


class CreateUser(Interactor[CreateUserDTO, UserId]):
    def __init__(
            self,
            user_gateway: UserGateway,
            password_hasher: PasswordHasher,
            transaction_manager: TransactionManager,
            user_service: UserService,
    ):
        self._user_gateway = user_gateway
        self._password_hasher = password_hasher
        self._transaction_manager = transaction_manager
        self._user_service = user_service


    async def __call__(self, dto: CreateUserDTO) -> UserId:
        hashed_password = self._password_hasher.hash_password(dto.password)
        user = self._user_service.create_user(
            age=dto.age,
            email=dto.email,
            username=dto.username,
            password=hashed_password,
        )
        await self._user_gateway.create_user(user)
        await self._transaction_manager.commit()
        return user.id

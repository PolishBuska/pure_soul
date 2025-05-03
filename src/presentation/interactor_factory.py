from abc import abstractmethod
from contextlib import asynccontextmanager
from typing import Protocol, runtime_checkable, Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.add_subscription import AddSubscription
from src.application.check_subscription import CheckSubscription
from src.application.common.id_provider import IdProvider
from src.application.common.transaction_manager import TransactionManager
from src.application.create_user import CreateUser


@runtime_checkable
class UserInteractorFactory(Protocol):

    @abstractmethod
    @asynccontextmanager
    async def create_user(
            self,
            uow: TransactionManager | AsyncSession
    ) -> CreateUser:
        raise NotImplementedError()

    @abstractmethod
    @asynccontextmanager
    async def create_artist(
            self,
            uow: TransactionManager
    ):
        raise NotImplementedError()

    async def __call__(self, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    @asynccontextmanager
    async def get_genres(self, uow):
        raise NotImplementedError()

    @abstractmethod
    @asynccontextmanager
    async def login_user(
            self,
            uow
    ):
        raise NotImplementedError()

    @abstractmethod
    @asynccontextmanager
    async def add_subscription(self, id_provider: IdProvider, uow: Any) -> AddSubscription:
        raise NotImplementedError()
    @abstractmethod
    @asynccontextmanager
    async def get_tiers(self, uow):
        raise NotImplementedError()

    @abstractmethod
    @asynccontextmanager
    async def check_subscription(self, id_provider: IdProvider, uow: Any) -> CheckSubscription:
        raise NotImplementedError()
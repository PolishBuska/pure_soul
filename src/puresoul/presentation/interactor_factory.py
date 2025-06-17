from abc import abstractmethod
from contextlib import asynccontextmanager
from typing import Protocol, runtime_checkable, Any

from sqlalchemy.ext.asyncio import AsyncSession

from puresoul.application.create_album import CreateAlbum
from src.puresoul.application.add_subscription import AddSubscription
from src.puresoul.application.check_subscription import CheckSubscription
from src.puresoul.application.common.id_provider import IdProvider
from src.puresoul.application.common.transaction_manager import TransactionManager
from src.puresoul.application.create_user import CreateUser
from src.puresoul.application.get_payment_types import GetPaymentTypes


@runtime_checkable
class UserInteractorFactory(Protocol):

    @abstractmethod
    @asynccontextmanager
    async def create_album(
            self,
            uow: TransactionManager,
            id_provider: IdProvider,
    ) -> CreateAlbum:
        raise NotImplementedError()

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

    @abstractmethod
    @asynccontextmanager
    async def get_payments_types(self, uow, id_provider: IdProvider) -> GetPaymentTypes:
        raise NotImplementedError()

    @abstractmethod
    @asynccontextmanager
    async def create_song(self, uow, id_provider: IdProvider):
        raise NotImplementedError()

    @abstractmethod
    @asynccontextmanager
    async def find_artists_by_names(self, uow):
        raise NotImplementedError()

    @abstractmethod
    @asynccontextmanager
    async def get_song(self, uow, id_provider: IdProvider):
        raise NotImplementedError()

    @abstractmethod
    @asynccontextmanager
    async def get_file(self):
        raise NotImplementedError()

    @abstractmethod
    @asynccontextmanager
    async def get_feed(self, uow):
        raise NotImplementedError()

    @abstractmethod
    @asynccontextmanager
    async def publish_album(self, uow, id_provider: IdProvider):
        raise NotImplementedError()

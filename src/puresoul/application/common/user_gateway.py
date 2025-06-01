from typing import Protocol, Dict, Any, List
from abc import abstractmethod

from src.puresoul.domain.artist import Artist
from src.puresoul.domain.iam.user import BaseUser, UserId
from src.puresoul.domain.types import ArtistId


class UserGateway(Protocol):

    @abstractmethod
    async def create_user(self, user: BaseUser) -> UserId:
        raise NotImplementedError()

    @abstractmethod
    async def get_user(self, user_id: int) -> BaseUser:
        raise NotImplementedError()

    @abstractmethod
    async def get_user_by_email(self, email: str) -> BaseUser:
        raise NotImplementedError()

    @abstractmethod
    async def create_artist(self, user: Artist) -> ArtistId:
        raise NotImplementedError()

    @abstractmethod
    async def find_artist_by_names(self, names: List[str]) -> List[Artist]:
        raise NotImplementedError()

    @abstractmethod
    async def filter_artists(self, params: Dict[str, Any]) -> List[Any]:
        raise NotImplementedError()

    @abstractmethod
    async def get_artist_by_user_id(self, user_id: UserId) -> Artist:
        raise NotImplementedError()

    @abstractmethod
    async def update_user(self, user: BaseUser) -> None:
        raise NotImplementedError()
    @abstractmethod
    async def update_user_sub(self, user: BaseUser):
        raise NotImplementedError()
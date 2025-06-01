from dataclasses import dataclass
from typing import List

from .common.id_provider import IdProvider
from .common.interactor import Interactor
from .common.transaction_manager import TransactionManager
from .common.user_gateway import UserGateway
from ..domain.artist import ArtistService
from ..domain.iam.exceptions import NotAuthorizedException, NotOldEnoughException
from ..domain.types import ArtistId


@dataclass
class CreateArtistDTO:
    artist_name: str
    artist_description: str
    gender: str
    age: int
    genres: List[int]


class CreateArtist(Interactor[CreateArtistDTO, ArtistId]):
    def __init__(
            self,
            id_provider: IdProvider,
            transaction_manager: TransactionManager,
            user_gateway: UserGateway,
            artist_service: ArtistService,
    ):
        self.id_provider = id_provider
        self.transaction_manager = transaction_manager
        self.user_gateway = user_gateway
        self.artist_service = artist_service


    async def __call__(self, dto: CreateArtistDTO) -> ArtistId:
        current_user = self.id_provider.get_current_user_id()
        if not current_user.can_access_premium_features():
            raise NotAuthorizedException(
                message=f'the current user: ` {current_user.id} `is not authorized to use this feature.',
            )
        if not current_user.is_adult:
            raise NotOldEnoughException(
                message=f'the current user: ` {current_user.id} `cannot use this feature. not an adult',
            )

        artist = self.artist_service.create_artist(
            user_id=current_user.id,
            artist_nickname=dto.artist_name,
            genres=dto.genres,
        )

        await self.user_gateway.create_artist(artist)
        await self.transaction_manager.commit()
        return artist.id

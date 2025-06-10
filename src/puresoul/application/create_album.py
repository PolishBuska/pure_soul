from puresoul.application.common.id_provider import IdProvider
from puresoul.application.common.interactor import Interactor
from puresoul.application.common.music_gateway import MusicGateway
from puresoul.application.common.user_gateway import UserGateway
from .common.dto import AlbumDTO
from .common.helpers import artists_exist
from .common.transaction_manager import TransactionManager
from ..domain.exceptions import NotAuthorizedException
from ..domain.song import SongService


class CreateAlbum(Interactor[AlbumDTO, None]):
    def __init__(
            self,
            id_provider: IdProvider,
            music_gateway: MusicGateway,
            user_gateway: UserGateway,
            song_service: SongService,
            transaction_manager: TransactionManager,
    ):
        self.id_provider = id_provider
        self.music_gateway = music_gateway
        self.user_gateway = user_gateway
        self.song_service = song_service
        self.transaction_manager = transaction_manager

    async def __call__(self, dto: AlbumDTO) -> None:
        current_user = self.id_provider.get_current_user_id()
        if not current_user.can_access_premium_features():
            raise NotAuthorizedException(
                "cannot access premium features",
            )
        if not artists_exist(
                user_gateway=self.user_gateway,
                artists=list(dto.artists),
        ):
            raise NotAuthorizedException(
                'cannot access artists',
            )
        album = await self.music_gateway.create_album(dto)
        print(album)
        await self.transaction_manager.commit()

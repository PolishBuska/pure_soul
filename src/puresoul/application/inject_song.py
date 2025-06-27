from dataclasses import dataclass
from typing import Tuple

from puresoul.application.common.id_provider import IdProvider
from puresoul.application.common.interactor import Interactor
from puresoul.application.common.music_gateway import MusicGateway
from puresoul.application.common.transaction_manager import TransactionManager
from puresoul.application.common.user_gateway import UserGateway

from puresoul.domain.exceptions import NotAuthorizedException
from puresoul.domain.album import Album
from puresoul.domain.song import SongService

@dataclass
class AlbumSongIds:
    album_id: int
    song_id: int

class InjectSong(Interactor[AlbumSongIds, Album]):
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

    async def __call__(self, album_song_ids: AlbumSongIds) -> None:
        current_user = self.id_provider.get_current_user_id()
        if not current_user.can_access_premium_features():
            raise NotAuthorizedException(
                "action not allowed",
            )
        album = await self.music_gateway.get_album_by_id(album_song_ids.album_id)
        if album.author_id != current_user.id:
            raise NotAuthorizedException(
                "action not allowed",
            )
        await self.music_gateway.inject_song(album, album_song_ids.song_id)
        await self.transaction_manager.commit()

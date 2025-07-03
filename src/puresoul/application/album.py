from dataclasses import dataclass
from typing import List

from puresoul.application.common.album_dto import AlbumsSearchParams
from puresoul.application.common.id_provider import IdProvider
from puresoul.application.common.interactor import Interactor
from puresoul.application.common.music_gateway import MusicGateway
from puresoul.application.common.transaction_manager import TransactionManager
from puresoul.domain.album import Album
from puresoul.domain.song import Song
from puresoul.domain.exceptions import NotAuthorizedException

class AlbumFeed(Interactor[AlbumsSearchParams, List[Album]]):
    def __init__(
            self,
            music_gateway: MusicGateway,
            id_provider: IdProvider,
            transaction_manager: TransactionManager
    ):
        self.music_gateway = music_gateway
        self.id_provider = id_provider
        self.transaction_manager = transaction_manager

    async def __call__(self, dto: AlbumsSearchParams) -> List[Album]:
        albums = await self.music_gateway.search_albums(dto)
        return albums


class AlbumSongs(Interactor[int, List[Song]]):

    def __init__(self, music_gateway: MusicGateway, id_provider: IdProvider):
        self.music_gateway = music_gateway
        self.id_provider = id_provider

    async def __call__(self,
            album_id: int
    ) -> List[Song]:
        user = self.id_provider.get_current_user_id()
        if not user.can_listen():
            raise NotAuthorizedException(
                "You are not authorized to use this functionality."
            )
        songs = await self.music_gateway.get_songs_by_album_id(album_id)
        return songs

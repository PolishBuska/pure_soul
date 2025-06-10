import asyncio
from dataclasses import dataclass
from typing import Optional, List

from .common.helpers import adapt_song_filepaths
from .common.file_storage import FileStorage
from .common.id_provider import IdProvider
from .common.interactor import Interactor
from .common.dto import DTO
from .common.music_gateway import MusicGateway
from .common.transaction_manager import TransactionManager
from ..domain.song import Song



@dataclass
class Feed(DTO):
    search: Optional[str]
    genres: Optional[List[int]]
    artists: Optional[List[int]]


class GetFeed(Interactor[Feed, List[Song]]):
    def __init__(
            self,
            song_file_storage: FileStorage,
            music_gateway: MusicGateway,
            transaction_manager: TransactionManager,
            id_provider: IdProvider,
            image_file_storage: FileStorage,
    ):
        self.song_file_storage = song_file_storage
        self.music_gateway = music_gateway
        self.transaction_manager = transaction_manager
        self.id_provider = id_provider
        self.image_file_storage = image_file_storage
    async def __call__(self, feed: Feed) -> List[Song]:
        songs = await self.music_gateway.search_songs(
            page_size=feed.page_size,
            page=feed.page,
            search=feed.search,
            genres=feed.genres,
            artists=feed.artists,
        )
        return songs

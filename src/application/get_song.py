import asyncio

from src.application.common.file_storage import FileStorage
from src.application.common.id_provider import IdProvider
from src.application.common.interactor import Interactor
from src.application.common.music_gateway import MusicGateway
from src.application.common.transaction_manager import TransactionManager
from src.domain.song import Song
from .common.helpers import adapt_song_filepaths


class GetSong(Interactor[int, Song]):
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

    async def __call__(self, song_id: int) -> Song:
        song = await self.music_gateway.get_song_by_id(song_id)
        return await adapt_song_filepaths(
            song,
            image_file_storage=self.image_file_storage,
            song_file_storage=self.song_file_storage
        )

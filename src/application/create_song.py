from dataclasses import dataclass
from io import BytesIO
from typing import List

from src.application.common.file_storage import FileStorage
from src.application.common.id_provider import IdProvider
from src.application.common.interactor import Interactor
from src.application.common.music_gateway import MusicGateway
from src.application.common.names_hasher import NamesHasher
from src.application.common.transaction_manager import TransactionManager
from src.application.common.user_gateway import UserGateway

from src.domain.exceptions import NotAuthorizedException
from src.domain.genre import Genre
from src.domain.song import SongService
from src.domain.types import SongTitle, SongDescription, SongCoverImage


@dataclass
class CreateSongDto:
    file: BytesIO
    name: str
    genres: List[Genre]
    cover_image_file: BytesIO
    authors: List[int]
    description: str

class CreateSong(Interactor[CreateSongDto, None]):
    def __init__(
            self,
            file_storage: FileStorage,
            music_gateway: MusicGateway,
            transaction_manager: TransactionManager,
            id_provider: IdProvider,
            song_service: SongService,
            names_hasher: NamesHasher,
            user_gateway: UserGateway,
    ):
        self.file_storage = file_storage
        self.music_gateway = music_gateway
        self.transaction_manager = transaction_manager
        self.id_provider = id_provider
        self.song_service = song_service
        self.names_hasher = names_hasher
        self.user_gateway = user_gateway

    async def __call__(self, dto: CreateSongDto) -> None:
        current_user = self.id_provider.get_current_user_id()
        if not current_user.can_access_premium_features():
            raise NotAuthorizedException(
                "cannot access premium features",
            )
        artists = await self.user_gateway.filter_artists(params={'id': dto.authors})
        for artist in artists:
            if artist not in dto.authors:
                raise NotAuthorizedException(f"Specified artist does not exist {artist}")
        cover_image_path = (
            f"{self.file_storage.root_path}"
            f"/{current_user.id}/"
            f".{self.names_hasher.hash_name(dto.cover_image_file.name)}/"
        )
        song_file_path = (
            f"{self.file_storage.root_path}"
            f"/{current_user.id}/{self.names_hasher.hash_name(dto.file.name)}"
        )
        song = self.song_service.create_song(
            title=SongTitle(dto.name),
            genres=dto.genres,
            description=SongDescription(dto.description),
            album_id=None,
            artists=dto.authors,
            cover_image=SongCoverImage(cover_image_path),
            created_at=None,
            updated_at=None,
            song_file_path=song_file_path,
            original_song_filename=dto.file.name,
            original_cover_image_filename=dto.cover_image_file.name,
        )
        await self.music_gateway.add_song(
            song=song,
        )

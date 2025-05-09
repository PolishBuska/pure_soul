from dataclasses import dataclass
from io import BytesIO
from typing import List, Tuple

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
class SongFiles:
    song: BytesIO
    cover_image: BytesIO

@dataclass
class CreateSongDto:
    name: str
    genres: List[int]
    authors: List[str]
    description: str

class CreateSong(Interactor[Tuple[CreateSongDto, SongFiles], None]):
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

    async def __call__(self, dto: Tuple[CreateSongDto, SongFiles]) -> None:
        current_user = self.id_provider.get_current_user_id()
        if not current_user.can_access_premium_features():
            raise NotAuthorizedException(
                "cannot access premium features",
            )
        artists = await self.user_gateway.filter_artists(
            params={
                'name': dto[0].authors
            }
        )
        is_artist = list(
            filter(
                lambda artist: artist.user_id == current_user.id, artists
            )
        ) if len(artists) > 0 else False
        if not is_artist:
            raise NotAuthorizedException(
                'not authorized',
            )
        cover_image_path = (
            f"{self.file_storage.root_path}"
            f"/{current_user.id}/"
            f".{self.names_hasher.hash_name(dto[1].cover_image.name)}/"
        )
        song_file_path = (
            f"{self.file_storage.root_path}"
            f"/{current_user.id}/{self.names_hasher.hash_name(dto[1].song.name)}"
        )
        song = self.song_service.create_song(
            title=SongTitle(dto[0].name),
            genres=dto[0].genres,
            description=SongDescription(dto[0].description),
            album_id=None,
            artists=dto[0].authors,
            cover_image=SongCoverImage(cover_image_path),
            created_at=None,
            updated_at=None,
            song_file_path=song_file_path,
            original_song_filename=dto[1].song.name,
            original_cover_image_filename=dto[1].cover_image.name,
            author_id=current_user.id
        )
        await self.music_gateway.add_song(
            song=song,
        )

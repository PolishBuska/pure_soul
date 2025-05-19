import asyncio
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
from src.domain.song import SongService
from src.domain.types import SongTitle, SongDescription, SongCoverImage
import struct

@dataclass
class SongFiles:
    song: BytesIO
    cover_image: BytesIO
    song_filename: str
    cover_image_filename: str

@dataclass
class CreateSongDto:
    name: str
    genres: List[int]
    authors: List[int]
    description: str

class CreateSong(Interactor[Tuple[CreateSongDto, SongFiles], None]):
    def __init__(
            self,
            song_file_storage: FileStorage,
            music_gateway: MusicGateway,
            transaction_manager: TransactionManager,
            id_provider: IdProvider,
            song_service: SongService,
            names_hasher: NamesHasher,
            user_gateway: UserGateway,
            image_file_storage: FileStorage,
    ):
        self.song_file_storage = song_file_storage
        self.music_gateway = music_gateway
        self.transaction_manager = transaction_manager
        self.id_provider = id_provider
        self.song_service = song_service
        self.names_hasher = names_hasher
        self.user_gateway = user_gateway
        self.image_file_storage = image_file_storage

    async def __call__(self, dto: Tuple[CreateSongDto, SongFiles]) -> None:
        current_user = self.id_provider.get_current_user_id()
        if not current_user.can_access_premium_features():
            raise NotAuthorizedException(
                "cannot access premium features",
            )
        artists = await self.user_gateway.filter_artists(
            params={
                'id': [int(author) for author in dto[0].authors]
            }
        )
        if not all(str(ar) for ar in artists if ar in dto[0].authors):
            raise NotAuthorizedException(
                'Cannot perform requested operation',
            )

        cover_image_path = (
            f"/{current_user.id}/"
            f".{self.names_hasher.hash_name(dto[1].cover_image_filename)}"
        )
        song_file_path = (
            f"/{current_user.id}/{self.names_hasher.hash_name(dto[1].song_filename)}"
        )
        song = self.song_service.create_song(
            title=SongTitle(dto[0].name),
            genres=[int(genre) for genre in dto[0].genres],
            description=SongDescription(dto[0].description),
            album_id=None,
            artists=dto[0].authors,
            cover_image=SongCoverImage(cover_image_path),
            created_at=None,
            updated_at=None,
            song_file_path=song_file_path,
            original_song_filename=dto[1].song_filename,
            original_cover_image_filename=dto[1].cover_image_filename,
            author_id=current_user.id
        )
        song_id = await self.music_gateway.add_song(
            song=song,
        )
        await asyncio.to_thread(
            self.song_file_storage.save_file,
            file_object=dto[1].song,
            obj_key=song_file_path + f"/{song_id}",
        )
        await asyncio.to_thread(
            self.image_file_storage.save_file,
            file_object=dto[1].cover_image,
            obj_key= f"/{song_id}/{cover_image_path}/{song_id}",
        )

        await self.transaction_manager.commit()

from dataclasses import dataclass
from io import BytesIO
from typing import List, Tuple, Optional

from puresoul.application.common.file_storage import FileStorage
from puresoul.application.common.helpers import (
    save_song_files,
    artists_exist,
    get_song_full_paths
)
from puresoul.application.common.id_provider import IdProvider
from puresoul.application.common.interactor import Interactor
from puresoul.application.common.music_gateway import MusicGateway
from puresoul.application.common.names_hasher import NamesHasher
from puresoul.application.common.transaction_manager import TransactionManager
from puresoul.application.common.user_gateway import UserGateway

from puresoul.domain.exceptions import NotAuthorizedException
from puresoul.domain.song import SongService
from puresoul.domain.types import SongTitle, SongDescription, SongCoverImage

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
    album_id: Optional[int]

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
        if not artists_exist(
            user_gateway=self.user_gateway,
            artists=dto[0].authors,
        ):
            raise NotAuthorizedException(
                'operation is not allowed',
            )
        if dto[0].album_id is not None:
            author_id = await self.music_gateway.get_album_author_id(album_id=dto[0].album_id)
            if not author_id == current_user.id:
                raise NotAuthorizedException(
                    'operation is not allowed',
                )
        cover_image_path, song_file_path = get_song_full_paths(
            hasher=self.names_hasher,
            curr_user=current_user.id,
            song_file_name=dto[1].song_filename,
            image_file_name=dto[1].cover_image_filename,
        )
        song = self.song_service.create_song(
            title=SongTitle(dto[0].name),
            genres=[int(genre) for genre in dto[0].genres],
            description=SongDescription(dto[0].description),
            album_id=dto[0].album_id,
            artists=dto[0].authors,
            cover_image=SongCoverImage(self.image_file_storage.root_path + cover_image_path),
            created_at=None,
            updated_at=None,
            song_file_path=f"{self.song_file_storage.root_path}/" + song_file_path,
            original_song_filename=dto[1].song_filename,
            original_cover_image_filename=dto[1].cover_image_filename,
            author_id=current_user.id
        )
        song_id = await self.music_gateway.add_song(
            song=song,
        )
        await save_song_files(
            song_file_storage=self.song_file_storage,
            cover_image_storage=self.image_file_storage,
            song=(song_file_path, dto[1].song, song_id),
            image_file=(cover_image_path, dto[1].cover_image, song_id),
        )
        await self.transaction_manager.commit()

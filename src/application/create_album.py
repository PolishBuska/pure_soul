import asyncio
from dataclasses import dataclass
from typing import List, Tuple

from src.application.common.file_storage import FileStorage
from src.application.common.id_provider import IdProvider
from src.application.common.interactor import Interactor
from src.application.common.music_gateway import MusicGateway
from src.application.common.user_gateway import UserGateway
from .common.helpers import artists_exist, get_song_full_paths, save_song_files
from .common.names_hasher import NamesHasher
from .common.transaction_manager import TransactionManager
from .create_song import CreateSongDto, SongFiles
from ..domain.album import Album
from ..domain.exceptions import NotAuthorizedException
from ..domain.song import SongService
from ..domain.types import ArtistId, AlbumTitle, AlbumDescription, SongTitle, SongDescription, SongCoverImage


@dataclass
class AlbumDTO:
    album_name: str
    album_description: str
    album_genres: List[int]
    album_songs: List[Tuple[
            CreateSongDto, SongFiles
        ]
    ]


class CreateAlbum(Interactor[AlbumDTO, None]):
    def __init__(
            self,
            image_file_storage: FileStorage,
            songs_storage: FileStorage,
            id_provider: IdProvider,
            music_gateway: MusicGateway,
            user_gateway: UserGateway,
            names_hasher: NamesHasher,
            song_service: SongService,
            transaction_manager: TransactionManager,
    ):
        self.file_storage = image_file_storage
        self.songs_storage = songs_storage
        self.id_provider = id_provider
        self.music_gateway = music_gateway
        self.user_gateway = user_gateway
        self.names_hasher = names_hasher
        self.song_service = song_service
        self.transaction_manager = transaction_manager

    async def __call__(self, dto: AlbumDTO) -> None:
        current_user = self.id_provider.get_current_user_id()
        if not current_user.can_access_premium_features():
            raise NotAuthorizedException(
                "cannot access premium features",
            )
        unique_artists = set([artist for so in dto.album_songs for artist in so[0].authors])
        if not artists_exist(
                user_gateway=self.user_gateway,
                artists=list(unique_artists),
        ):
            raise NotAuthorizedException(
                'cannot access artists',
            )
        songs= []
        upload_tasks = []
        for song_dto, song_files in dto.album_songs:
            cover_image_path, song_file_path = get_song_full_paths(
                hasher=self.names_hasher,
                curr_user=current_user.id,
                song_file_name=song_files.song_filename,
                image_file_name=song_files.cover_image_filename,
            )
            song = self.song_service.create_song(
                title=SongTitle(song_dto.name),
                genres=[int(genre) for genre in song_dto.genres],
                description=SongDescription(song_dto.description),
                album_id=None,
                artists=song_dto.authors,
                cover_image=SongCoverImage(self.file_storage.root_path + cover_image_path),
                created_at=None,
                updated_at=None,
                song_file_path=f"{self.songs_storage.root_path}/" + song_file_path,
                original_song_filename=song_files.song_filename,
                original_cover_image_filename=song_files.cover_image_filename,
                author_id=current_user.id
            )
            songs.append(
                song
            )
        persisted_songs = await self.music_gateway.add_songs(
            songs=songs,
        )
        persisted_songs_with_files = list(zip(persisted_songs, dto.album_songs))
        for upload in persisted_songs_with_files:
            upload_tasks.append(
                save_song_files(
                    song_file_storage=self.songs_storage,
                    cover_image_storage=self.file_storage,
                    song=(
                        upload[0].song_file_path.removeprefix(
                            f"{self.songs_storage.root_path}/"
                        ), upload[1][1].song, upload[0].id),
                    image_file=(
                        upload[0].cover_image.removeprefix(
                            f"{self.file_storage.root_path}/"
                        ), upload[1][1].cover_image, upload[0].id
                    ),
                )
            )
        album = Album(
            artists_ids=list(ArtistId(ar) for ar in unique_artists),
            id=None,
            title=AlbumTitle(dto.album_name),
            description=AlbumDescription(dto.album_description),
            genres=dto.album_genres,
            songs=songs,
        )
        album.id = await self.music_gateway.create_album(album)
        await asyncio.gather(*upload_tasks)
        await self.transaction_manager.commit()

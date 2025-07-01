from typing import Protocol, List
from abc import abstractmethod

from puresoul.application.common.dto import AlbumDTO
from src.puresoul.domain.album import Album
from src.puresoul.domain.genre import Genre
from src.puresoul.domain.song import Song


class MusicGateway(Protocol):

    @abstractmethod
    async def add_song(self, song: Song):
        raise NotImplementedError()

    @abstractmethod
    async def get_genres(self) -> list[Genre]:
        raise NotImplementedError()

    @abstractmethod
    async def get_users_tracks(
            self,
            genres: List[int],
            artists: List[int],
    ) -> List[Song]:
        raise NotImplementedError()

    @abstractmethod
    async def get_playlists_with_tracks_existing(
            self,
            tracks: List[Song],
            page: int,
            page_size: int,
    ):
        raise NotImplementedError()

    @abstractmethod
    async def get_playlists(
            self,
            page: int,
            page_size: int,
            genres: List[int],
            artists: List[int],
    ):
        raise NotImplementedError()

    @abstractmethod
    async def get_song_by_id(
            self,
            song_id: int,
    ) -> Song:
        raise NotImplementedError()

    @abstractmethod
    async def search_songs(
            self,
            page: int,
            page_size: int,
            genres: List[int],
            artists: List[int],
            search: str
    ):
        raise NotImplementedError()

    @abstractmethod
    async def create_album(self, album: AlbumDTO) -> Album:
        raise NotImplementedError()

    @abstractmethod
    async def fetch_artists(self, artists: List[int]):
        raise NotImplementedError()

    @abstractmethod
    async def fetch_genres(self, genres: List[int]):
        raise NotImplementedError()

    @abstractmethod
    async def add_songs(self, songs: List[Song]) -> List[Song]:
        raise NotImplementedError()

    @abstractmethod
    async def get_album_by_id(
            self,
            album_id: int,
    ) -> Album:
        raise NotImplementedError()

    @abstractmethod
    async def get_album_author_id(
            self,
            album_id: int,
    ):
        raise NotImplementedError()

    @abstractmethod
    async def update_album(self, album: Album):
        raise NotImplementedError()

    @abstractmethod
    async def add_songs_to_album(self, album: Album, song_ids: List[int]):
        raise NotImplementedError()

    @abstractmethod
    async def get_songs_in(
            self,
            song_ids: List[int],
    ):
        raise NotImplementedError()

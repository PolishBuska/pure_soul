from typing import Protocol, List
from abc import abstractmethod

from src.domain.genre import Genre
from src.domain.song import Song


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
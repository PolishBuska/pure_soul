from dataclasses import dataclass
from typing import List, Optional

from .common.id_provider import IdProvider
from .common.interactor import Interactor
from .common.music_gateway import MusicGateway
from ..domain.playlist import Playlist


@dataclass
class PlaylistsDTO:
    genres_ids: Optional[List[int]]
    name: Optional[str]
    artists: Optional[List[int]]
    relevant: bool
    page: int
    page_size: int

class GetPlaylists(Interactor[PlaylistsDTO, List[Playlist]]):
    def __init__(
            self,
            music_gateway: MusicGateway,
            id_provider: IdProvider,
    ):
        self.music_gateway = music_gateway
        self.id_provider = id_provider


    async def __call__(self, dto: PlaylistsDTO) -> List[Playlist]:
        if dto.relevant:
            users_tracks = await self.music_gateway.get_users_tracks(
                genres=dto.genres_ids,
                artists=dto.artists,
            )
            playlists = await self.music_gateway.get_playlists_with_tracks_existing(
                tracks=users_tracks,
                page_size=dto.page_size,
                page=dto.page,
            )
            songs = set(users_tracks)
            prioritized_playlists = []
            for playlist in playlists:
                priority = [pl_so for pl_so in playlist.songs if pl_so in songs]
                prioritized_playlists.append(
                    (len(priority), playlist),
                )
            prioritized_playlists.sort(key=lambda pl: pl[0], reverse=True)

            return [plist for _, plist in prioritized_playlists]
        else:
            playlists = await self.music_gateway.get_playlists(
                genres=dto.genres_ids,
                artists=dto.artists,
                page_size=dto.page_size,
                page=dto.page,
            )
            return playlists

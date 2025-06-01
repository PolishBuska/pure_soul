from dataclasses import dataclass
from typing import List, Optional

from .genre import Genre
from .song import Song
from .types import UserId, PlaylistId

@dataclass
class Playlist:
    playlist_id: Optional[PlaylistId]
    songs: List[Song]
    genres: List[Genre]
    author_id: UserId


class PlaylistService:
    def create_playlist(
            self,
            songs: List[Song],
            genres: List[Genre],
            author_id: UserId
    ) -> Playlist:
        return Playlist(
            playlist_id=None,
            songs=songs,
            genres=genres,
            author_id=author_id
        )

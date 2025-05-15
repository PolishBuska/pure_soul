from dataclasses import dataclass
from typing import List, Optional

from src.domain.iam.user import UserId
from .exceptions import TooManyGenresException
from .genre import Genre

from .types import ArtistId, ArtistNickname, GenreId
from .album import Album


@dataclass(frozen=False, eq=True, unsafe_hash=True)
class Artist:
    id: Optional[ArtistId]
    user_id: UserId
    nickname: ArtistNickname
    genres: List[Genre]


@dataclass(frozen=True, eq=True, unsafe_hash=True)
class ArtistDashboard:
    artist_id: ArtistId
    albums: List[Album]

class ArtistService:
    def create_artist(
            self,
            user_id: UserId,
            artist_nickname: str,
            genres: Optional[List[int]] = None,
    ) -> Artist:
        if len(genres) > 15:
            raise TooManyGenresException(
                f"Could not create artist with {len(genres)} genres. Too long"
            )
        return Artist(
            id=None,
            user_id=user_id,
            nickname=ArtistNickname(artist_nickname),
            genres=genres,
        )

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from .artist import Artist
from .exceptions import NotAuthorizedException, TooFewItemsException, AlreadyPublic
from .genre import Genre
from .iam.user import BaseUser
from .types import (
    AlbumId,
    AlbumDescription,
    AlbumTitle,
)
from .song import Song

@dataclass
class Album:
    id: Optional[AlbumId]
    title: AlbumTitle
    description: AlbumDescription
    genres: List[Genre]
    songs: Optional[List[Song]]
    artists: List[Artist]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    is_released: bool
    author_id: int

    def publish_album(
            self,
            cu: BaseUser
    ) -> None:
        """
            This function will publish the requested album
            This function doesn't return anything
            It will publish the requested album by changing its internal state

            :param cu: The one whose requesting a publishing
            :return: None
        """
        if self.author_id != cu.id:
            raise NotAuthorizedException(
                "cannot access this feature"
            )
        if len(self.songs) <= 3:
            raise TooFewItemsException(
                "too few songs to publish, please populate the album"
            )
        if self.is_released:
            raise AlreadyPublic(
                "this album is already released"
            )
        self.is_released = True

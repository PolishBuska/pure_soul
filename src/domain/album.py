from dataclasses import dataclass
from typing import List

from .types import (
    AlbumId,
    AlbumDescription,
    AlbumTitle,
    AlbumCoverImage, ArtistId,
)
from .song import Song

@dataclass
class Album:
    id: AlbumId
    title: AlbumTitle
    description: AlbumDescription
    cover_picture: AlbumCoverImage
    songs: List[Song]
    artists_ids: List[ArtistId]

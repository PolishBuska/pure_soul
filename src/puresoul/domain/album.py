from dataclasses import dataclass
from typing import List, Optional

from .types import (
    AlbumId,
    AlbumDescription,
    AlbumTitle,
    AlbumCoverImage, ArtistId,
)
from .song import Song

@dataclass
class Album:
    id: Optional[AlbumId]
    title: AlbumTitle
    description: AlbumDescription
    genres: List[int]
    songs: Optional[List[Song]]
    artists_ids: List[ArtistId]

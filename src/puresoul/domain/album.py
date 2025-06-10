from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from .artist import Artist
from .genre import Genre
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
    genres: List[Genre]
    songs: Optional[List[Song]]
    artists: List[Artist]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    is_released: bool

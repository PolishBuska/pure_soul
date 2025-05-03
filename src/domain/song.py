from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

from src.domain.exceptions import DomainException

from .types import (
    SongTitle,
    SongId,
    SongDescription,
    AlbumId,
    SongCoverImage,
    ArtistId,
)
from .genre import Genre

@dataclass
class Song:
    title: SongTitle
    id: Optional[SongId]
    description: Optional[SongDescription]
    album_id: Optional[AlbumId]
    cover_image: Optional[SongCoverImage]
    artists: List[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    genres: Optional[List[Genre]]
    song_file_path: str
    original_song_filename: str
    original_cover_image_filename: str

class SongService:
    def create_song(
            self,
            title: SongTitle,
            description: Optional[SongDescription],
            album_id: Optional[AlbumId],
            cover_image: Optional[SongCoverImage],
            artists: List[str],
            created_at: Optional[datetime],
            updated_at: Optional[datetime],
            genres: Optional[List[Genre]],
            song_file_path: str,
            original_song_filename: Optional[str],
            original_cover_image_filename: Optional[str],
    ) -> Song:
        if len(title) > 255:
            raise DomainException(
                "The song's title cannot exceed 255 characters."
            )
        return Song(
            title=title,
            description=description,
            album_id=album_id,
            cover_image=cover_image,
            artists=artists,
            created_at=created_at,
            updated_at=updated_at,
            genres=genres,
            id=None,
            song_file_path=song_file_path,
            original_song_filename=original_song_filename,
            original_cover_image_filename=original_cover_image_filename,
        )

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
    author_id: Optional[int]

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "album_id": self.album_id,
            "cover_image": self.cover_image,
            "artists": [(ar.nickname, ar.id) for ar in self.artists],
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
            "genres": [(sg.name, sg.genre_id) for sg in self.genres],
            "song_file_path": self.song_file_path,
            "original_song_filename": self.original_song_filename,
            "original_cover_image_filename": self.original_cover_image_filename,
            "author_id": self.author_id
        }

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
            genres: Optional[List[int]],
            song_file_path: str,
            original_song_filename: Optional[str],
            original_cover_image_filename: Optional[str],
            author_id: int
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
            author_id=author_id
        )

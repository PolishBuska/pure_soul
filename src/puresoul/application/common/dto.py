from dataclasses import dataclass
from typing import Optional, List


@dataclass
class DTO:
    page: Optional[int]
    page_size: Optional[int]


@dataclass
class AlbumDTO:
    album_name: str
    album_description: str
    album_genres: List[int]
    artists: List[int]
    author_id: int
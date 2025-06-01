from dataclasses import dataclass
from datetime import datetime

from .types import GenreId, GenreName


@dataclass
class Genre:
    name: GenreName
    genre_id: GenreId
    created_at: datetime
    updated_at: datetime

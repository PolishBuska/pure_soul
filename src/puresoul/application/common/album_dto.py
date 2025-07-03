from dataclasses import dataclass
from typing import List

from puresoul.application.common.dto import DTO


@dataclass
class AlbumsSearchParams(DTO):
    name: str
    genres: List[int]
    artists: List[int]
    newest: bool

from typing import List

from .common.music_gateway import MusicGateway
from .common.id_provider import IdProvider
from ..domain.exceptions import NotAuthorizedException
from ..domain.genre import Genre


class GetGenres:
    def __init__(self, music_gateway: MusicGateway, id_provider: IdProvider):
        self.music_gateway = music_gateway
        self.id_provider = id_provider

    async def __call__(self) -> List[Genre]:
        current_user = self.id_provider.get_current_user_id()
        if not current_user.can_listen():
            raise NotAuthorizedException("Not enough permissions")
        genres = await self.music_gateway.get_genres()
        return genres

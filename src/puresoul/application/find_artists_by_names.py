from typing import List

from .common.interactor import Interactor
from .common.user_gateway import UserGateway
from ..domain.artist import Artist


class FindArtistsByNames(Interactor[List[str], List[Artist]]):
    def __init__(
            self,
            user_gateway: UserGateway,
    ):
        self.user_gateway = user_gateway

    async def __call__(self, names: List[str]) -> List[Artist]:
        res = await self.user_gateway.find_artist_by_names(names)
        return res
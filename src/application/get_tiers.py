from typing import List

from src.domain.subscription.tiers import SubscriptionTier

from .common.tiers_gateway import TiersGateway
from .common.interactor import Interactor

class GetTiers(Interactor[None, List[SubscriptionTier]]):
    def __init__(self, tiers_gateway: TiersGateway):
        self._tiers_gateway = tiers_gateway

    async def __call__(self, *args, **kwargs) -> List[SubscriptionTier]:
        tiers = await self._tiers_gateway.get_tiers()
        return tiers

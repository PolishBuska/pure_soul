from abc import abstractmethod
from typing import Protocol, List

from src.puresoul.domain.subscription.tiers import SubscriptionTier

class TiersGateway(Protocol):

    @abstractmethod
    async def get_tier_by_id(self, tier_id: int) -> SubscriptionTier:
        raise NotImplementedError

    @abstractmethod
    async def get_tiers(self) -> List[SubscriptionTier]:
        raise NotImplementedError

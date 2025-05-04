from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.common.tiers_gateway import TiersGateway
from src.domain.subscription.tiers import SubscriptionTier

from .tables import TierTable

class SQLATierGateway(TiersGateway):
    def __init__(self, uow: AsyncSession):
        self.uow = uow
    async def get_tier_by_id(self, tier_id: int) -> SubscriptionTier:
        query = select(TierTable).where(TierTable.id == tier_id)
        res = await self.uow.scalar(query)
        return res.to_domain()

    async def get_tiers(self) -> List[SubscriptionTier]:
        query = select(TierTable).order_by(TierTable.price.asc())
        res = await self.uow.scalars(query)
        return [tier.to_domain() for tier in res]

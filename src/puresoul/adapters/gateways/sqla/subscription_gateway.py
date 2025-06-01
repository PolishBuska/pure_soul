from typing import List

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from puresoul.adapters.gateways.sqla.tables import SubscriptionTable
from puresoul.application.common.subscription_gateway import SubscriptionGateway
from puresoul.domain.subscription.model import ActiveSubscription


class SQLASubscriptionGateway(SubscriptionGateway):
    def __init__(self, uow: AsyncSession):
        self._uow = uow

    async def get_subscriptions(self) -> List[ActiveSubscription]:
        query = select(SubscriptionTable)
        res = await self._uow.scalars(query)
        return [data.to_domain() for data in res]

    async def get_subscription_by_user_id(self, user_id: int) -> ActiveSubscription:
        query = select(SubscriptionTable).where(SubscriptionTable.user_id == user_id)
        res = await self._uow.scalar(query)
        return res.to_domain()

    async def save_subscription(self, subscription: ActiveSubscription) -> int:
        stmt = insert(SubscriptionTable).values(
            user_id=subscription.user_id,
            started_at=subscription.started_at,
            ended_at=subscription.ended_at,
            tier_id=subscription.tier_id,
            payment_id=subscription.payment_id,
            payment_method=subscription.payment_method
        ).returning(SubscriptionTable.id)
        op = await self._uow.execute(stmt)
        flushed_id = op.scalar_one_or_none()
        return flushed_id

    async def get_subscription_by_id(self, subscription_id: int) -> ActiveSubscription:
        query = select(SubscriptionTable).where(SubscriptionTable.id == subscription_id)
        res = await self._uow.scalar(query)
        return res.to_domain()
    async def get_subscription(self, **kwargs) -> ActiveSubscription:
        ...

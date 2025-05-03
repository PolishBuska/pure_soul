from typing import List

from typing_extensions import Protocol
from abc import abstractmethod

from src.domain.subscription.model import ActiveSubscription


class SubscriptionGateway(Protocol):
    @abstractmethod
    async def get_subscriptions(self) -> List[ActiveSubscription]:
        raise NotImplementedError()

    @abstractmethod
    async def get_subscription(self, **kwargs) -> ActiveSubscription:
        raise NotImplementedError()

    @abstractmethod
    async def save_subscription(self, subscription: ActiveSubscription) -> int:
        raise NotImplementedError()

    @abstractmethod
    async def get_subscription_by_id(self, subscription_id: int) -> ActiveSubscription:
        raise NotImplementedError()
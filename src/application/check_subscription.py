from .common.id_provider import IdProvider
from .common.interactor import Interactor
from .common.subscription_gateway import SubscriptionGateway
from ..domain.subscription.model import ActiveSubscription


class CheckSubscription(Interactor[None, ActiveSubscription | None]):
    def __init__(self, subscription_gateway: SubscriptionGateway, id_provider: IdProvider):
        self._subscription_gateway = subscription_gateway
        self.id_provider = id_provider
    async def __call__(self, *args, **kwargs) -> ActiveSubscription | None:
        user = self.id_provider.get_current_user_id()
        if user.subscription_id is None:
            return None
        else:
            subscription = await self._subscription_gateway.get_subscription_by_id(user.subscription_id)
            return subscription

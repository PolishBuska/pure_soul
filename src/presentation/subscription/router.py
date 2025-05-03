from typing import Any

from litestar import Router, Controller, Request, post, get

from src.application.add_subscription import CardSubscription, CryptoSubscription
from src.application.common.id_provider import IdProvider
from src.domain.subscription.model import ActiveSubscription
from src.presentation.interactor_factory import UserInteractorFactory


class SubscriptionController(Controller):

    @get('/tiers')
    async def get_tiers(
            self,
            uow_factory: Any,
            interactor_factory: UserInteractorFactory
    ) -> Any:
        async with interactor_factory.get_tiers(uow=uow_factory) as interactor:
            return await interactor()

    @get('')
    async def check_subscription(
            self,
            uow_factory: Any,
            interactor_factory: UserInteractorFactory,
            id_provider: IdProvider,
            request: Request,
    ) -> ActiveSubscription:
        async with interactor_factory.check_subscription(
                uow=uow_factory,
                id_provider=id_provider(request=request),
        ) as interactor:
            return await interactor()

    @post('')
    async def add_subscription(
            self,
            interactor_factory: UserInteractorFactory,
            uow_factory: Any,
            data: CardSubscription | CryptoSubscription,
            id_provider: IdProvider,
            request: Request,
    ) -> None:
        async with interactor_factory.add_subscription(
                uow=uow_factory,
                id_provider=id_provider(request),
        ) as interactor:
            return await interactor(
                subscription=data,
            )

subscription_router = Router(
    route_handlers=[SubscriptionController],
    path='/subscription',
)
import uuid
from dataclasses import dataclass

from .common.id_provider import IdProvider

from .common.interactor import Interactor
from .common.payment_gateway import PaymentGateway
from .common.payment_provider import PaymentProvider
from .common.subscription_gateway import SubscriptionGateway
from .common.tiers_gateway import TiersGateway
from .common.transaction_manager import TransactionManager
from .common.user_gateway import UserGateway
from src.domain.iam.constants import Grants
from src.domain.iam.user import UserService
from src.domain.subscription.model import SubscriptionService



@dataclass
class Subscription:
    tier_choice: int
    payment_choice: int

@dataclass
class CardSubscription(Subscription):
    card_number: str
    card_holder_fullname: str
    card_expiry: str
    card_security_code: str

@dataclass
class CryptoSubscription(Subscription):
    crypto_code: str

class AddSubscription(Interactor[CardSubscription | CryptoSubscription, None]):
    def __init__(
            self,
            user_gateway: UserGateway,
            transaction_manager: TransactionManager,
            user_service: UserService,
            payment_provider: PaymentProvider,
            id_provider: IdProvider,
            tiers_gateway: TiersGateway,
            subscription_gateway: SubscriptionGateway,
            subscription_service: SubscriptionService,
            payment_gateway: PaymentGateway,
    ):
        self._user_gateway = user_gateway
        self._transaction_manager = transaction_manager
        self._user_service = user_service
        self._payment_provider = payment_provider
        self._id_provider = id_provider
        self._tiers_gateway = tiers_gateway
        self._subscription_gateway = subscription_gateway
        self._subscription_service = subscription_service
        self._payment_gateway = payment_gateway


    async def __call__(self, subscription: CardSubscription | CryptoSubscription) -> None:
        current_user = self._id_provider.get_current_user_id()
        async with self._payment_provider as payment:
            tier = await self._tiers_gateway.get_tier_by_id(subscription.tier_choice)
            payment_info = await self._payment_gateway.get_payment(subscription.payment_choice)
            payment_id = await payment.pay(amount=tier.price, payment_info=payment_info)
            subscription = self._subscription_service.create_subscription(
                payment_id=payment_id,
                user_id=current_user.id,
                ending_threshold=tier.ending_threshold,
                tier_id=tier.id,
            )
            current_user.grants.extend(
                [
                    Grants.CAN_ACCESS_PREMIUM_FEATURES,
                    Grants.CAN_DOWNLOAD_SONGS,
                    Grants.CAN_SKIP_ADS,
                    Grants.CAN_CREATE_PLAYLIST
                ]
            )
            subscription_id = await self._subscription_gateway.save_subscription(subscription)
            current_user.subscription_id = subscription_id
            await self._user_gateway.update_user_sub(current_user)
            await self._transaction_manager.commit()

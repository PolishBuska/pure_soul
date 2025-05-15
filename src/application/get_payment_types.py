from typing import List

from src.domain.subscription.choices import PaymentChoice

from .common.interactor import Interactor
from .common.payment_gateway import PaymentGateway
from ..domain.subscription.payment_choice import Payment


class GetPaymentTypes(Interactor[None, PaymentChoice]):
    def __init__(
            self,
            payment_gateway: PaymentGateway,
    ):
        self._payment_gateway = payment_gateway

    async def __call__(self, *args, **kwargs) -> List[Payment]:
        payment_types = await self._payment_gateway.get_payments_types()
        return payment_types

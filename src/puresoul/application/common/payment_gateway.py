from typing import Protocol, List
from abc import abstractmethod

from src.puresoul.domain.subscription.payment_choice import Payment


class PaymentGateway(Protocol):
    @abstractmethod
    async def get_payments_types(self) -> List[Payment]:
        raise NotImplementedError

    @abstractmethod
    async def get_payment(self, id_: int):
        raise NotImplementedError

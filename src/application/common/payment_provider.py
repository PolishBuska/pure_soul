from abc import abstractmethod
from typing import Protocol, NewType, Tuple
from decimal import Decimal

from src.domain.subscription.payment_choice import Payment

PaymentPrint = NewType("PaymentPrint", str)
PaymentId = NewType("PaymentId", str)

class PaymentProvider(Protocol):

    @abstractmethod
    async def __aenter__(self) -> "PaymentProvider":
        raise NotImplementedError()

    @abstractmethod
    async def pay(self, amount: Decimal, payment_info: Payment, **kwargs) -> Tuple[PaymentId, PaymentPrint]:
        raise NotImplementedError()

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError()
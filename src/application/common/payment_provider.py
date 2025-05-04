from abc import abstractmethod
from typing import Protocol
from decimal import Decimal

from src.domain.subscription.choices import PaymentChoice
from src.domain.subscription.payment_choice import Payment


class PaymentProvider(Protocol):

    @abstractmethod
    async def __aenter__(self) -> "PaymentProvider":
        raise NotImplementedError()

    @abstractmethod
    async def pay(self, amount: Decimal, payment_info: Payment) -> str:
        raise NotImplementedError()

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError()
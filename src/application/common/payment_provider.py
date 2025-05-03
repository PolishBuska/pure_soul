from abc import abstractmethod
from typing import Protocol
from decimal import Decimal

from src.domain.subscription.choices import PaymentChoice

class PaymentProvider(Protocol):

    @abstractmethod
    async def __aenter__(self) -> "PaymentProvider":
        raise NotImplementedError()

    @abstractmethod
    async def pay(self, amount: Decimal, payment_info: PaymentChoice) -> str:
        raise NotImplementedError()

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError()
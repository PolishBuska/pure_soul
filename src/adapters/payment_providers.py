from _decimal import Decimal

from src.application.common.payment_provider import PaymentProvider
from src.domain.subscription.choices import PaymentChoice


class SomeFakeAssPaymentProvider(PaymentProvider):
    def __init__(self):
        self._last_amount: Decimal|None = None
        self._last_payment_info: PaymentChoice|None = None

    async def pay(self, amount: Decimal, payment_info: PaymentChoice) -> str:
        self._last_amount = amount
        self._last_payment_info = payment_info
        return "fake-payment-id"

    async def cancel(self) -> str:
        if self._last_amount is None or self._last_payment_info is None:
            raise RuntimeError("No payment to cancel.")

        return "fake-cancel-id"

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.cancel()

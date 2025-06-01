import uuid
from _decimal import Decimal
from typing import Tuple

from puresoul.application.common.payment_provider import PaymentProvider, PaymentPrint, PaymentId
from puresoul.domain.subscription.payment_choice import Payment


class SomeFakeAssPaymentProvider(PaymentProvider):
    def __init__(self):
        self._last_amount: Decimal|None = None
        self._last_payment_info: Payment|None = None

    async def pay(self, amount: Decimal, payment_info: Payment, **kwargs) -> Tuple[PaymentId, PaymentPrint]:
        self._last_amount = amount
        self._last_payment_info = payment_info
        payment_id = PaymentId(str(uuid.uuid4()))
        payment_print_str = PaymentPrint("".join(f"{k}={v}" for k, v in kwargs.items()))
        return payment_id, payment_print_str

    async def cancel(self) -> str:
        if self._last_amount is None or self._last_payment_info is None:
            raise RuntimeError("No payment to cancel.")

        return "fake-cancel-id"

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.cancel()

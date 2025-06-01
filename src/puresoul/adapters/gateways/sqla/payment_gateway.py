from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from puresoul.adapters.gateways.sqla.tables import PaymentChoices
from puresoul.application.common.payment_gateway import PaymentGateway
from puresoul.domain.subscription.payment_choice import Payment


class SaPaymentGateway(PaymentGateway):
    def __init__(self, uow: AsyncSession):
        self.uow = uow

    async def get_payments_types(self) -> List[Payment]:
        query = select(PaymentChoices).order_by(PaymentChoices.id)
        result = await self.uow.scalars(query)
        return [pa_choice.to_domain() for pa_choice in result]

    async def get_payment(self, id_: int) -> Payment:
        query = select(PaymentChoices).where(PaymentChoices.id == id_)
        result = await self.uow.scalar(query)
        return result.to_domain()

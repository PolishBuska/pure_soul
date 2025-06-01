from typing import Any, List

from litestar import Controller, Router, get, Request

from src.puresoul.application.common.id_provider import IdProvider
from src.puresoul.domain.genre import Genre
from src.puresoul.presentation.interactor_factory import UserInteractorFactory


class GenresController(Controller):
    path = ''

    @get('')
    async def list_genres(self,
            request: Request,
            interactor_factory: UserInteractorFactory,
            uow_factory: Any,
            id_provider: IdProvider,
    ) -> List[Genre]:
        async with interactor_factory.get_genres(
            uow=uow_factory,
            id_provider=id_provider(request=request),
        ) as interactor:
            return await interactor()

genres_router = Router(
    route_handlers=[GenresController],
    path='/genres',
)

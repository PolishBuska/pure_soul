from typing import Any
from litestar import Request
from litestar import Controller, post, Router

from src.application.common.id_provider import IdProvider
from src.application.create_artist import CreateArtistDTO
from src.presentation.interactor_factory import UserInteractorFactory



class ArtistController(Controller):
    path = ''
    @post('')
    async def create_artist(
            self,
            data: CreateArtistDTO,
            interactor_factory: UserInteractorFactory,
            uow_factory: Any,
            id_provider: IdProvider,
            request: Request,
    ) -> None:
        async with interactor_factory.create_artist(uow=uow_factory, id_provider=id_provider(request)) as interactor:
            res = await interactor(dto=data)
            return res


artist_router = Router(
    path='/artist',
    route_handlers=[ArtistController]
)
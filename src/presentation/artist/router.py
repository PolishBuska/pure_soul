from typing import Any, List, Annotated
from litestar import Request, get, Controller, post, Router
from litestar.params import Parameter
from pydantic import BaseModel, Field

from src.application.common.id_provider import IdProvider
from src.application.create_artist import CreateArtistDTO
from src.presentation.interactor_factory import UserInteractorFactory


class ArtistNameDTO(BaseModel):
    name: str = Field(min_length=1, max_length=100)


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

    @get('')
    async def get_artists_by_names(
            self,
            names: List[str],
            interactor_factory: UserInteractorFactory,
            uow_factory: Any,
    ) -> None:
        async with interactor_factory.find_artists_by_names(uow=uow_factory) as interactor:
            res = await interactor(names=names)
            return res



artist_router = Router(
    path='/artist',
    route_handlers=[ArtistController]
)
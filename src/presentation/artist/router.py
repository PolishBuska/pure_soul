from litestar import Controller, post, Router
from litestar.dto import DataclassDTO

from src.application.common.transaction_manager import TransactionManager
from src.application.create_artist import CreateArtistDTO
from src.presentation.interactor_factory import UserInteractorFactory



class ArtistController(Controller):
    path = ''
    CreateArtistDTO = DataclassDTO[CreateArtistDTO]
    @post('')
    async def create_artist(
            self,
            data: CreateArtistDTO,
            interactor_factory: UserInteractorFactory,
            uow_factory: TransactionManager,
    ) -> None:
        async with interactor_factory.create_artist(uow=uow_factory) as interactor:
            res = await interactor(dto=data)
            return res


artist_router = Router(
    path='/artist',
    route_handlers=[ArtistController]
)
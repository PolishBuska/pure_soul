from typing import Any, Dict

from src.puresoul.application.create_user import CreateUserDTO
from src.puresoul.application.login_user import LoginUserDTO

from src.puresoul.presentation.interactor_factory import MainInteractorFactory


class UserController(Controller):
    path = '/user'
    UserDTO = DataclassDTO[CreateUserDTO]

    @post('')
    async def create_user(
            self,
            data: CreateUserDTO,
            interactor_factory: MainInteractorFactory,
            uow_factory: Any,
    ) -> int:
        async with interactor_factory.create_user(
            uow=uow_factory,
        ) as interactor:
            return await interactor(dto=data)

    @post('/login', openapi={"security": []})
    async def login(
            self,
            interactor_factory: MainInteractorFactory,
            uow_factory: Any,
            data: LoginUserDTO = Body(media_type="application/x-www-form-urlencoded"),
    ) -> Dict:
        async with interactor_factory.login_user(uow=uow_factory) as interactor:
            result = await interactor(dto=data)
            return {
                'access_token': result.access_token,
                'type': "bearer",
            }



user_router = Router(
    route_handlers=[UserController],
    path='/iam',
)

from typing import Any, Dict

from litestar import Controller, Router, post
from litestar.dto import DataclassDTO
from litestar.params import Body

from src.puresoul.application.create_user import CreateUserDTO
from src.puresoul.application.login_user import LoginUserDTO

from src.puresoul.presentation.interactor_factory import UserInteractorFactory


class UserController(Controller):
    path = '/user'
    UserDTO = DataclassDTO[CreateUserDTO]

    @post('')
    async def create_user(
            self,
            data: CreateUserDTO,
            interactor_factory: UserInteractorFactory,
            uow_factory: Any,
    ) -> int:
        async with interactor_factory.create_user(
            uow=uow_factory,
        ) as interactor:
            return await interactor(dto=data)

    @post('/login', openapi={"security": []})
    async def login(
            self,
            interactor_factory: UserInteractorFactory,
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

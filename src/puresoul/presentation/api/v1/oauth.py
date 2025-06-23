from typing import Annotated

from fastapi import APIRouter, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from puresoul.application.common.transaction_manager import TransactionManager
from puresoul.application.login_user import LoginUserDTO
from puresoul.presentation.interactor_factory import MainInteractorFactory


def create_auth_router() -> APIRouter:
    router = APIRouter()

    class OAuthResponse(BaseModel):
        access_token: str
        type: str

    async def oauth(
            ioc: Annotated[MainInteractorFactory, Depends()],
            uow: Annotated[TransactionManager, Depends()],
            creds: Annotated[OAuth2PasswordRequestForm, Depends()],
    ) -> OAuthResponse:
        async with ioc.login_user(uow=uow) as interactor:
            res = await interactor(dto=LoginUserDTO(
                    username=creds.username,
                    password=creds.password,
                )
            )
            return OAuthResponse(
                access_token=res.access_token,
                type="bearer",
            )
    router.add_api_route(
        '/oauth',
        endpoint=oauth,
        methods=['POST'],
    )
    return router

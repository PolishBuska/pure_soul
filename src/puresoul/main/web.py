import logging
from contextlib import asynccontextmanager
from typing import Annotated, Callable

import uvicorn
from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request
from starlette.responses import FileResponse
from uvicorn import Server

from puresoul.adapters.file_storage import Boto3FileStorage
from puresoul.adapters.gateways.sqla.uow import SqlaUOW
from puresoul.adapters.id_provider import JWTIdProvider
from puresoul.adapters.password_hasher import BcryptPasswordHasher, BcryptNamesHasher
from puresoul.adapters.payment_providers import SomeFakeAssPaymentProvider
from puresoul.adapters.token_generator import JoseTokenGenerator
from puresoul.application.common.id_provider import IdProvider
from puresoul.application.common.transaction_manager import TransactionManager
from puresoul.domain.artist import ArtistService
from puresoul.domain.exceptions import (
    DomainException
)
from puresoul.domain.iam.user import UserService
from puresoul.domain.song import SongService
from puresoul.domain.subscription.model import SubscriptionService
from puresoul.main.ioc import WebIoc
from puresoul.presentation.interactor_factory import MainInteractorFactory
from puresoul.presentation.api.v1.main import create_main_router
from puresoul.presentation.api.v1.exc_handlers.exception_handler import handle_exceptions


def app_factory(
        interactor_factory: MainInteractorFactory,
        id_provider: Callable[[str], JWTIdProvider],
) -> FastAPI:
    app = FastAPI()
    app.dependency_overrides.update(
        {
            MainInteractorFactory: interactor_factory,
            IdProvider: id_provider,
        }
    )
    return app



@asynccontextmanager
async def start_server(
        app: FastAPI,
        db_url: str,
) -> Server:
    """
    This function manages the application's start
    """
    logger = logging.getLogger("uvicorn")

    config = uvicorn.Config(
        app,
        host="localhost",
        port=8080,
        reload=False,
    )
    uow: TransactionManager | SqlaUOW = SqlaUOW(db_url)
    server = Server(config)

    logger.info(f"Initialized Server with config: {config.host} : {config.port}")

    logger.info(f"DB healthcheck")

    await uow.healthcheck()

    logger.info(f"DB is healthy")

    app.dependency_overrides.update(
        {
            TransactionManager: uow.get_session_factory
        }
    )
    yield server
    await uow.shutdown()
    logger.info(f"uvicorn server stopped")
    logger.info(f"connections are shut down")
    await server.shutdown()

async def protected(request: Request, id_provider: Annotated[IdProvider, Depends()]):
    return id_provider.get_current_user_id()

async def main() -> None:
    db_url = 'postgresql+asyncpg://admin:admin123@localhost:5432/pure_soul'
    token_secret = 'secret'
    s3_uri = 'http://127.0.0.1:9000'
    s3_access_key_id = 'mRa7SfDQPxvAr7OX1loRaAyfHf2JX4PC9iqhBUU8'
    s3_secret_key = 'cPXy2dJM4im3iRjApIWw'
    ioc = WebIoc(
        user_service=UserService(),
        password_hasher=BcryptPasswordHasher(),
        art_service=ArtistService(),
        song_file_storage=Boto3FileStorage(
            s3_uri=s3_uri,
            aws_access_key_id=s3_access_key_id,
            aws_secret_access_key=s3_secret_key,
            bucket_name='songs',
        ),
        song_service=SongService(),
        names_hasher=BcryptNamesHasher(),
        token_generator=JoseTokenGenerator(
            secret=token_secret,
        ),
        payment_provider=SomeFakeAssPaymentProvider(),
        subscription_service=SubscriptionService(),
        image_file_storage=Boto3FileStorage(
            s3_uri=s3_uri,
            aws_access_key_id=s3_access_key_id,
            aws_secret_access_key=s3_secret_key,
            bucket_name='images',
        )
    )

    current_prefix = '/api/v1'

    oauth2_scheme = OAuth2PasswordBearer(
        tokenUrl=current_prefix + '/oauth',
    )


    def inject_token(
            token: Annotated[str, Depends(oauth2_scheme)],
    ) -> JWTIdProvider:
        return JWTIdProvider(token_secret)(token)

    async def root():
        return FileResponse(
            path='src/puresoul/main/root.html'
        )
    app = app_factory(
        interactor_factory=ioc,
        id_provider=inject_token,
    )
    app.add_api_route(
        '/',
        endpoint=root,
    )
    app.add_api_route(
        '/internal/protected',
        endpoint=protected,
        methods=['GET'],
        name='internal-protected',
        include_in_schema=True,
        dependencies=[Depends(inject_token)],
    )
    app.include_router(
        create_main_router(
            prefix=current_prefix,
            token_handler=inject_token,
            audio_formats=frozenset({'audio/mpeg', 'audio/mp3', 'audio/wav'}),
            image_formats=frozenset({'image/png', 'image/jpeg'}),
        )
    )
    app.add_exception_handler(DomainException, handle_exceptions)
    async with start_server(app, db_url) as server:
        await server.serve()

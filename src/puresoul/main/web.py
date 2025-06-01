
import uvicorn
from litestar import Litestar, Request
from litestar.di import Provide
from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import SwaggerRenderPlugin
from litestar.openapi.spec import Components, SecurityScheme, OAuthFlows, OAuthFlow
from litestar.response import Response

from puresoul.adapters.file_storage import Boto3FileStorage
from puresoul.adapters.id_provider import provide_jwt_id_provider
from puresoul.adapters.password_hasher import BcryptPasswordHasher, BcryptNamesHasher
from puresoul.adapters.payment_providers import SomeFakeAssPaymentProvider
from puresoul.adapters.token_generator import JoseTokenGenerator
from puresoul.domain.artist import ArtistService
from puresoul.domain.exceptions import DomainException, NotAuthenticatedException
from puresoul.domain.iam.user import UserService
from puresoul.domain.song import SongService
from puresoul.domain.subscription.model import SubscriptionService
from puresoul.main.ioc import WebIoc

from puresoul.presentation.router import main_router
from puresoul.adapters.gateways.sqla.uow import SqlaUOW

EXC_MAP = {
    DomainException: 500,
    NotAuthenticatedException: 401
}

def handle_domain_errors(request: Request, exc: DomainException) -> Response:
    if isinstance(exc, DomainException):
        exc_code = EXC_MAP.get(exc.__class__)

        response = Response(
            status_code=exc_code,
            content={
                "message": exc.message,
                "exc_type": exc.type
            }
        )
        print(response.status_code)
        return response
    else:
        return Response(
            status_code=500,
            content={
                "message": "Internal Server Error"
            }
        )

def app_factory(
        db_url: str,
        secret: str,
        s3_access_key: str,
        s3_secret_key: str,
        s3_uri: str,
        song_bucket_name: str,
        image_bucket_name: str,
        audio_formats,
        image_formats,
) -> Litestar:
    app = Litestar(
        openapi_config=OpenAPIConfig(
            title="My API",
            version="1.0.0",
            render_plugins=[SwaggerRenderPlugin()],
            security=[{"OAuth2Password": []}],
            components=Components(
    security_schemes={
        "OAuth2Password": SecurityScheme(
            type="oauth2",
            flows=OAuthFlows(
                password=OAuthFlow(
                    scopes={},
                    token_url="/api/v1/iam/user/login",
                )
            ),
            description="Use your credentials to get a JWT token."
        ),
    }
),

        ),
        dependencies={
            "interactor_factory": Provide(WebIoc(
                user_service=UserService(),
                password_hasher=BcryptPasswordHasher(),
                art_service=ArtistService(),
                song_file_storage=Boto3FileStorage(
                    bucket_name=song_bucket_name,
                    s3_uri=s3_uri,
                    aws_access_key_id=s3_access_key,
                    aws_secret_access_key=s3_secret_key
                ),
                song_service=SongService(),
                names_hasher=BcryptNamesHasher(),
                token_generator=JoseTokenGenerator(
                    secret=secret,
                ),
                payment_provider=SomeFakeAssPaymentProvider(),
                subscription_service=SubscriptionService(),
                image_file_storage=Boto3FileStorage(
                    bucket_name=image_bucket_name,
                    s3_uri=s3_uri,
                    aws_access_key_id=s3_access_key,
                    aws_secret_access_key=s3_secret_key
                )

            )),
            "uow_factory": Provide(SqlaUOW(db_url=db_url).get_session_factory),
            "id_provider": Provide(provide_jwt_id_provider(secret)),
            "audio_formats": Provide(audio_formats),
            "image_formats": Provide(image_formats),
        },
        debug=True,
        exception_handlers={
            DomainException: handle_domain_errors
        },

    )
    return app

async def start_server(
        app: Litestar,
) -> None:
    """
    This function manages the application's start
    """

    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8080,
        reload=False,
    )
    server = uvicorn.Server(config)
    await server.serve()

async def main() -> None:
    class AudioFormats:
        def __call__(self):
            return  {'audio/mpeg', 'audio/mp3', 'audio/wav'}
    class ImageFormats:
        def __call__(self):
            return {'image/png', 'image/jpeg'}
    db_url = 'postgresql+asyncpg://admin:admin123@localhost:5432/pure_soul'
    token_secret = 'secret'
    s3_uri = 'http://127.0.0.1:9000'
    s3_access_key_id = 'mRa7SfDQPxvAr7OX1loRaAyfHf2JX4PC9iqhBUU8'
    s3_secret_key = 'cPXy2dJM4im3iRjApIWw'

    app = app_factory(
        db_url=db_url,
        secret=token_secret,
        s3_access_key=s3_access_key_id,
        s3_secret_key=s3_secret_key,
        s3_uri=s3_uri,
        song_bucket_name='songs',
        image_bucket_name='images',
        audio_formats=AudioFormats(),
        image_formats=ImageFormats(),
    )
    app.register(main_router)
    await start_server(app)

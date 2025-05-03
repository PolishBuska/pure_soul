
import uvicorn
from litestar import Litestar, Request
from litestar.di import Provide
from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import SwaggerRenderPlugin
from litestar import status_codes
from litestar.openapi.spec import Components, SecurityScheme, OAuthFlows, OAuthFlow
from litestar.response import Response


from src.adapters.gateways.http.s3_file_storage import S3FileStorage
from src.adapters.id_provider import provide_jwt_id_provider
from src.adapters.password_hasher import BcryptPasswordHasher, BcryptNamesHasher
from src.adapters.payment_providers import SomeFakeAssPaymentProvider
from src.adapters.token_generator import JoseTokenGenerator
from src.domain.artist import ArtistService
from src.domain.exceptions import DomainException, NotAuthenticatedException
from src.domain.iam.user import UserService
from src.domain.song import SongService
from src.domain.subscription.model import SubscriptionService
from src.main.ioc import WebIoc

from src.presentation.router import main_router
from src.adapters.gateways.sqla.uow import SqlaUOW

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

def app_factory(db_url: str, secret: str) -> Litestar:
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
                file_storage=S3FileStorage('govno'),
                song_service=SongService(),
                names_hasher=BcryptNamesHasher(),
                token_generator=JoseTokenGenerator(
                    secret=secret,
                ),
                payment_provider=SomeFakeAssPaymentProvider(),
                subscription_service=SubscriptionService()

            )),
            "uow_factory": Provide(SqlaUOW(db_url=db_url).get_session_factory),
            "id_provider": Provide(provide_jwt_id_provider(secret)),
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
        host="localhost",
        port=8080,
        reload=False,
    )
    server = uvicorn.Server(config)
    await server.serve()

async def main() -> None:
    db_url = 'postgresql+asyncpg://admin:admin123@localhost:5432/pure_soul'
    token_secret = 'secret'

    app = app_factory(db_url=db_url, secret=token_secret)
    app.register(main_router)
    await start_server(app)

import dataclasses
import random
from typing import Dict, Any, Annotated

from litestar import Router, get, post
from litestar.params import Body
from litestar.response import Response

from .user.router import user_router
from .artist.router import artist_router
from .genres.router import genres_router
from .subscription.router import subscription_router
@dataclasses.dataclass(frozen=True)
class DebugValues:
    str_sep_by_comma: str

@dataclasses.dataclass(frozen=True)
class RequestDebug:
    value: Dict[str, Any]

@get('/', sync_to_thread=False)
def root() -> Response:
    return Response(content='hit /schema for documentation')

@post('/debug',
      sync_to_thread=False,
      response_description='values of a json separated by comma',
)
def debug(
        data: Annotated[RequestDebug, Body()],
) -> DebugValues:
    return DebugValues(
        str_sep_by_comma=", ".join(v for v in data.value.values()),
    )

@get('/debug/randint/{limit:int}', sync_to_thread=False)
def randint(limit: int) -> Response:
    res = random.randint(1, limit)
    return Response(content=str(res))

@get('/debug/greet', sync_to_thread=False)
def greet(name: str) -> Response:
    return Response(content={'data': f'Hello, {name}!'})

main_router = Router(
    path='/api/v1',
    route_handlers=[
        root,
        debug,
        randint,
        greet,
        user_router,
        artist_router,
        genres_router,
        subscription_router
    ],
)

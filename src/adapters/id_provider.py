from typing import Any

from litestar import Request
from typing import Callable


from jose import jwt, ExpiredSignatureError, JWTError
from litestar.di import Provide

from src.application.common.id_provider import IdProvider
from src.domain.exceptions import NotAuthenticatedException
from src.domain.iam.user import BaseUser



class JWTIdProviderWithRequest(IdProvider):
    def __init__(self, secret: str):
        self._secret = secret

    def get_current_user_id(self) -> BaseUser:
        try:
            token: str = self._request.headers.get('authorization', None)
            if token is None:
                raise NotAuthenticatedException("Not authenticated")
            token = token.removeprefix("Bearer ")
            payload = jwt.decode(
                token,
                self._secret,
                algorithms=["HS256"]
            )
            return BaseUser(
                id=payload["user_id"],
                grants=payload.get("grants", []),
                is_adult=payload.get("is_adult", False),
                subscription_id=payload.get("subscription_id"),
                username=payload.get("username"),
                email=payload.get("email"),
                password=None
            )
        except ExpiredSignatureError:
            raise NotAuthenticatedException("Token has expired")
        except JWTError:
            raise NotAuthenticatedException("Invalid token")
    def __call__(self, request: Provide(Request)) -> Any:
        self._request = request
        return self

def provide_jwt_id_provider(secret: str) -> Callable[[Request], JWTIdProviderWithRequest]:
    def _provider(request: Request) -> JWTIdProviderWithRequest:
        return JWTIdProviderWithRequest(secret)(request)
    return _provider
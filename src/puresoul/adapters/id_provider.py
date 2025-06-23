from typing import Any

import jose

from jose import jwt, ExpiredSignatureError
from starlette.requests import Request

from puresoul.application.common.id_provider import IdProvider
from puresoul.domain.exceptions import NotAuthenticatedException
from puresoul.domain.iam.user import BaseUser



class JWTIdProvider(IdProvider):
    def __init__(self, secret: str):
        self._secret = secret

    def get_current_user_id(self) -> BaseUser:
        try:
            token: str = self._token
            if token is None:
                raise NotAuthenticatedException("Not authenticated")
            token = token.removeprefix("Bearer ")
            payload = jwt.decode(
                token,
                self._secret,
                algorithms=["HS256"],
                options={
                    "verify_exp": True,
                    'verify_iat': True,
                }
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
        except jose.JWTError:
            raise NotAuthenticatedException("Invalid token")
    def __call__(self, token: str) -> Any:
        self._token = token
        return self

from datetime import datetime, timedelta, timezone
from jose import jwt
from uuid import uuid4

from src.application.common.id_provider import Token
from src.application.common.token_generator import TokenGenerator
from src.domain.iam.user import BaseUser


class JoseTokenGenerator(TokenGenerator):
    def __init__(self, secret: str):
        self.__secret = secret
        self.algorithm = "HS256"

    def generate_tokens(self, user: BaseUser) -> Token:
        now = datetime.now(timezone.utc)

        access_token_payload = {
            "user_id": user.id,
            "grants": user.grants,
            "is_adult": user.is_adult,
            "subscription_id": user.subscription_id,
            "username": user.username,
            "email": user.email,
            "exp": now + timedelta(minutes=15),
            "iat": now,
            "type": "access"
        }

        access_token = jwt.encode(
            access_token_payload,
            self.__secret,
            algorithm=self.algorithm
        )

        refresh_token_payload = {
            "user_id": user.id,
            "exp": now + timedelta(days=7),
            "iat": now,
            "type": "refresh",
            "jti": str(uuid4()),
        }

        refresh_token = jwt.encode(
            refresh_token_payload,
            self.__secret,
            algorithm=self.algorithm
        )

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
        )

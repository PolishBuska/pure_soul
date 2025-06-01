from typing import Protocol

from .id_provider import Token
from ...domain.iam.user import BaseUser


class TokenGenerator(Protocol):

    def generate_tokens(
            self,
            user: BaseUser
    ) -> Token:
        raise NotImplementedError()

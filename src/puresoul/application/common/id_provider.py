from dataclasses import dataclass
from abc import abstractmethod, ABC
from typing import Protocol, Any

from src.puresoul.domain.iam.user import BaseUser


class IdProvider(ABC):

    @abstractmethod
    def get_current_user_id(self) -> BaseUser:
        raise NotImplementedError

    @abstractmethod
    def __call__(self, request: Any):
        raise NotImplementedError

@dataclass
class Token:
    access_token: str
    refresh_token: str

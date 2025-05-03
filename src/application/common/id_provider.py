from dataclasses import dataclass
from abc import abstractmethod
from typing import Protocol, Any, runtime_checkable

from src.domain.iam.user import BaseUser


@runtime_checkable
class IdProvider(Protocol):

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

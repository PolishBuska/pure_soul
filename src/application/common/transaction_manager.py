from abc import abstractmethod, ABC
from typing import Protocol, runtime_checkable

@runtime_checkable
class TransactionManager(Protocol):
    def __init__(self, uow) -> None:
        self.uow = uow
    async def commit(self) -> None:
        raise NotImplementedError

    async def flush(self) -> None:
        raise NotImplementedError

    async def rollback(self) -> None:
        raise NotImplementedError

    async def __call__(self, *args, **kwargs):
        raise NotImplementedError
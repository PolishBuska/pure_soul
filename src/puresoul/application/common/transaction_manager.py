from abc import ABC

class TransactionManager(ABC):
    async def commit(self) -> None:
        raise NotImplementedError

    async def flush(self) -> None:
        raise NotImplementedError

    async def rollback(self) -> None:
        raise NotImplementedError

    async def __call__(self, *args, **kwargs):
        raise NotImplementedError
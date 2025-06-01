from typing import Protocol

from abc import abstractmethod

class NamesHasher(Protocol):
    @abstractmethod
    def hash_name(self, name: str) -> str:
        raise NotImplementedError()
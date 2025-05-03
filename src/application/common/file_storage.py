from dataclasses import dataclass
from io import BytesIO
from typing import Protocol, NewType, List, Tuple
from abc import abstractmethod

@dataclass
class RootPath:
    path: str

    def __post_init__(self):
        if not self.path.startswith("/"):
            self.path = "/" + self.path

class FileStorage(Protocol):

    @abstractmethod
    async def get_all_paths(self, root: RootPath) -> List[str]:
        raise NotImplementedError()

    @abstractmethod
    async def save_file(self, file_object: BytesIO, bucket_name: str, file_id) -> str:
        raise NotImplementedError()

    @property
    @abstractmethod
    def root_path(self) -> str:
        raise NotImplementedError()

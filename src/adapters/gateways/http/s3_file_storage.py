from io import BytesIO
from typing import List, Tuple

from src.application.common.file_storage import FileStorage, RootPath


class S3FileStorage(FileStorage):
    def __init__(self, backet_name: str):
        self.backet_name = backet_name
    async def get_all_paths(self, root: RootPath) -> List[str]:
        ...
    async def get_path(self, path: str) -> str:
        ...
    async def get_paths(self, root: RootPath) -> List[str]:
        ...
    async def save_file(self, data: Tuple[str, BytesIO]) -> None:
        ...

    def root_path(self) -> str:
        ...
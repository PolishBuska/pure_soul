import asyncio
from io import BytesIO
from typing import Tuple

from puresoul.application.common.file_storage import FileStorage
from puresoul.application.common.interactor import Interactor


class DownloadPresignedUrl(Interactor[str, BytesIO]):
    def __init__(
            self,
            file_storage: FileStorage,
    ):
        self.file_storage = file_storage

    async def __call__(self, presigned_url: str) -> Tuple[BytesIO, str]:
        url_parts = presigned_url.split('/')
        bucket = url_parts[0]
        self.file_storage.root_path = bucket
        res = await asyncio.to_thread(self.file_storage.get_file, presigned_url.replace(bucket, ""))
        return res, bucket

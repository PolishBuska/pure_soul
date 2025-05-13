from io import BytesIO
from typing import List

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from src.application.common.file_storage import FileStorage, RootPath


class Boto3FileStorage(FileStorage):
    def __init__(
            self,
            s3_uri: str,
            aws_access_key_id: str,
            aws_secret_access_key: str,
            bucket_name: str,
    ):
        self.bucket_name = bucket_name
        self.s3_uri = s3_uri
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=aws_secret_access_key,
            aws_secret_access_key=aws_access_key_id,
            endpoint_url=s3_uri,
            region_name='us-east-1',
            config=Config(
                connect_timeout=5, read_timeout=10
            )
        )

    def save_file(
            self,
            file_object: BytesIO,
            obj_key: str,
    ) -> None:
        try:
            self.s3.upload_fileobj(
                file_object,
                self.root_path,
                obj_key
            )
        except ClientError as e:
            raise e

    def get_all_paths(self, root: RootPath) -> List[str]:
        return ['','']

    def root_path(self) -> str:
        return self.s3_uri

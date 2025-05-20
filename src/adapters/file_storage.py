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
            print(obj_key)
            self.s3.upload_fileobj(
                file_object,
                self.root_path,
                obj_key,
            ExtraArgs={"ContentType": "audio/mpeg"}
            )
        except ClientError as e:
            raise e

    def get_all_paths(self, root: RootPath) -> List[str]:
        return ['','']

    @property
    def root_path(self) -> str:
        return self.bucket_name

    def get_file(self, obj_key: str) -> BytesIO:
        no_leading_ = obj_key.lstrip("/")
        s3_prefetch = self.s3.list_objects_v2(
            Bucket=self.bucket_name,
            Prefix=no_leading_
        )
        path = s3_prefetch['Contents'][0]['Key']
        file_ob = BytesIO()
        self.s3.download_fileobj(
            self.root_path,
            path,
            file_ob
        )
        file_ob.seek(0)
        return file_ob

    def get_path(self, obj_key: str) -> str:
        no_leading_ = obj_key.lstrip("/")
        s3_prefetch = self.s3.list_objects_v2(
            Bucket=self.bucket_name,
            Prefix=no_leading_
        )
        path = s3_prefetch['Contents'][0]['Key']
        return path

    @root_path.setter
    def root_path(self, path: str) -> None:
        self.bucket_name = path

from io import BytesIO

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from src.application.common.file_storage import FileStorage


class boto3FileStorage(FileStorage):
    def __init__(
            self,
            s3_uri: str,
    ):
        self.s3_uri = s3_uri
        self.s3 = boto3.client(
            's3',
            aws_access_key_id='adminuser',
            aws_secret_access_key='adminuser',
            endpoint_url=s3_uri,
            region_name='us-east-1',
            config=Config(
                connect_timeout=5, read_timeout=10
            )
        )

    async def save_song(
            self,
            file_object: BytesIO,
            bucket_name: str,
            file_id: str,
            author_id: str
    ) -> str:
        try:
            self.s3.upload_fileobj(
                file_object,
                bucket_name,
                file_id
            )
            return f"{self.s3_uri}/{bucket_name}/{author_id}/{file_id}"
        except ClientError as e:
            raise e

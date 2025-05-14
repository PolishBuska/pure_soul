from contextlib import AsyncExitStack
from io import BytesIO
from typing import Any, List, Annotated, Set

from litestar.di import Provide
from pydantic import BaseModel, ConfigDict

from litestar import Controller, post, Router, Request
from litestar.datastructures import UploadFile
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.exceptions import HTTPException

from src.application.common.id_provider import IdProvider
from src.application.create_song import SongFiles, CreateSongDto
from src.presentation.inmemory_file_converter import to_bytesio_async
from src.presentation.interactor_factory import UserInteractorFactory


def validate_file_type(file: UploadFile, allowed_types: set[str]) -> UploadFile:
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {file.content_type}. Allowed types: {', '.join(allowed_types)}"
        )
    return file


class SongFormData(BaseModel):
    name: str
    authors: List[str]
    genres: List[str]
    description: str
    song: UploadFile
    cover_image: UploadFile
    model_config = ConfigDict(arbitrary_types_allowed=True)

class MusicController(Controller):

    @post(
        '',
        content_encoding=RequestEncodingType.MULTI_PART
    )
    async def create_song(
        self,
        id_provider: IdProvider,
        request: Request,
        interactor_factory: UserInteractorFactory,
        uow_factory: Any,
        data: Annotated[SongFormData, Body(media_type=RequestEncodingType.MULTI_PART)],
        audio_formats: Set[str],
        image_formats: Set[str],
    ) -> None:
        song = validate_file_type(data.song, audio_formats)
        cover_image = validate_file_type(data.cover_image, image_formats)

        create_dto = CreateSongDto(
            name=data.name,
            authors=data.authors,
            genres=data.genres,
            description=data.description
        )
        async with interactor_factory.create_song(id_provider=id_provider(request), uow=uow_factory) as interactor:
            async with to_bytesio_async(song.file) as song_bytesio, to_bytesio_async(cover_image.file) as cover_image_bytesio:
                return await interactor(
                    (
                        create_dto,
                        SongFiles(
                            song=song_bytesio,
                            cover_image=cover_image_bytesio,
                            song_filename=song.filename,
                            cover_image_filename=cover_image.filename,
                        )
                    )
                )

music_router = Router(
    route_handlers=[MusicController],
    path='/music',
    tags=['music management']
)
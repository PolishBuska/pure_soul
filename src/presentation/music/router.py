from typing import Any, List, Annotated
from pydantic import BaseModel, Field, ConfigDict

from litestar import Controller, post, Router, Request
from litestar.datastructures import UploadFile
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.exceptions import HTTPException

from src.application.common.id_provider import IdProvider
from src.application.create_song import SongFiles, CreateSongDto
from src.presentation.interactor_factory import UserInteractorFactory


def validate_file_type(file: UploadFile, allowed_types: set[str]) -> UploadFile:
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {file.content_type}. Allowed types: {', '.join(allowed_types)}"
        )
    return file


class CreateSongFormDTO(BaseModel):
    title: str
    name: str
    authors: List[int]
    genres: List[int]
    song: UploadFile
    cover_image: UploadFile
    description: str
    model_config = ConfigDict(arbitrary_types_allowed=True)


class MusicController(Controller):

    @post('')
    async def create_song(
        self,
        interactor_factory: UserInteractorFactory,
        uow_factory: Any,
        form: Annotated[CreateSongFormDTO, Body(media_type=RequestEncodingType.MULTI_PART)],
        id_provider: IdProvider,
        request: Request,
    ) -> None:
        song = validate_file_type(form.song, {'audio/mpeg', 'audio/mp3', 'audio/wav'})
        cover_image = validate_file_type(form.cover_image, {'image/jpeg', 'image/png'})

        create_dto = CreateSongDto(
            name=form.name,
            authors=form.authors,
            genres=form.genres,
            description=form.description
        )

        async with interactor_factory.create_song(id_provider=id_provider(request), uow=uow_factory) as interactor:
            return await interactor(
                (create_dto, SongFiles(song=song.file, cover_image=cover_image.file))
            )
music_router = Router(
    route_handlers=[MusicController],
    path='/music',
    tags=['music management']
)
from io import BytesIO
from typing import Any, List, Annotated, Set, Optional, Tuple

from litestar.response.streaming import Stream
from pydantic import BaseModel, ConfigDict, Field, field_validator

from litestar import Controller, post, Router, Request, get, patch
from litestar.datastructures import UploadFile
from litestar.enums import RequestEncodingType
from litestar.params import Body, Parameter
from litestar.exceptions import HTTPException

from puresoul.application.common.dto import AlbumDTO
from src.puresoul.application.get_feed import Feed

from src.puresoul.application.common.id_provider import IdProvider
from src.puresoul.application.create_song import SongFiles, CreateSongDto
from src.puresoul.domain.song import Song
from src.puresoul.presentation.inmemory_file_converter import spooled_to_bytesio, convert_bytesio_to_file_response
from src.puresoul.presentation.interactor_factory import UserInteractorFactory


def validate_file_type(file: UploadFile, allowed_types: set[str]) -> UploadFile:
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {file.content_type}. Allowed types: {', '.join(allowed_types)}"
        )
    return file


class AlbumModel(BaseModel):
    album_name: str = Field(min_length=1, max_length=100)
    album_description: str = Field(min_length=1, max_length=350)
    album_genres: List[int]
    album_artists: List[int]

    @field_validator("album_genres", mode='before')
    def validate_genres(cls, v):
        if len(v) == 0:
            raise ValueError("Genres cannot be an empty list")
        if len(v) > 100:
            raise ValueError("album_genres cannot exceed 100 characters")
        if any(isinstance(v, str) for v in v):
            raise ValueError("album_genres should be a list of integers")
        return v




class SongFormData(BaseModel):
    name: str
    authors: str
    genres: str
    description: str
    album_id: Optional[int] = None
    song: UploadFile
    cover_image: UploadFile
    model_config = ConfigDict(arbitrary_types_allowed=True)

class MusicController(Controller):

    @patch('/album/{album_id:int}')
    async def publish_album(
            self,
            album_id: int,
            request: Request,
            interactor_factory: UserInteractorFactory,
            uow_factory: Any,
            id_provider: IdProvider
    ) -> None:
        async with interactor_factory.publish_album(uow=uow_factory, id_provider=id_provider(request)) as interactor:
            return await interactor(album_id)

    @post('/album')
    async def create_album(self,
        id_provider: IdProvider,
        request: Request,
        interactor_factory: UserInteractorFactory,
        uow_factory: Any,
        data: AlbumModel) -> None:
        async with interactor_factory.create_album(uow=uow_factory, id_provider=id_provider(request)) as interactor:
            res = await interactor(
                AlbumDTO(
                    album_name=data.album_name,
                    album_description=data.album_description,
                    album_genres=data.album_genres,
                    artists=data.album_artists,
                )
            )
            return res
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
            authors=[int(el) for el in data.authors.split(',')],
            genres=[int(el) for el in data.genres.split(',')],
            description=data.description,
            album_id=data.album_id
        )
        async with interactor_factory.create_song(id_provider=id_provider(request), uow=uow_factory) as interactor:
            async with spooled_to_bytesio(song.file) as song_bytesio, spooled_to_bytesio(cover_image.file) as cover_image_bytesio:
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
    @get(
        '/{song_id:int}'
    )
    async def get_song(
            self,
            id_provider: IdProvider,
            request: Request,
            interactor_factory: UserInteractorFactory,
            uow_factory: Any,
            song_id: int,
    ) -> Song:
        async with interactor_factory.get_song(id_provider=id_provider(request), uow=uow_factory) as interactor:
            return await interactor(song_id)

    @get(
        '/feed',
        description='Get feed of all songs',
    )
    async def get_feed(
            self,
            interactor_factory: UserInteractorFactory,
            uow_factory: Any,
            id_provider: IdProvider,
            request: Request,
            page: int = Parameter(
                description='The page number to start from.',
                default=1,
                gt=0
            ),
            page_size: int = Parameter(
                le=15,
                description='The page size to start from.',
                default=10,
                gt=0
            ),
            search: str = Parameter(
                description='The search string to search for.',
                min_length=0,
                max_length=100,
            ),
            artists: Optional[List[int]] = Parameter(
                description='The artists to include in the query.',
                min_items=0,
                max_items=100,
            ),
            genres: Optional[List[int]] = Parameter(
                description='The genres to include in the query.',
                min_items=0,
                max_items=100,
            )
    ) -> List[Song]:
        async with interactor_factory.get_feed(
                uow=uow_factory,
                id_provider=id_provider(request),
        ) as interactor:
            return await interactor(
                Feed(
                    page=page,
                    page_size=page_size,
                    search=search,
                    artists=artists,
                    genres=genres,
                )
            )

    @get('/file')
    async def get_file(self, url: str, interactor_factory: UserInteractorFactory) -> Stream:
        async with interactor_factory.get_file() as interactor:
            """
                file: Tuple[BytesIO, str] = await interactor(url)
                    it returns the source of the file.
                    and the file stream.
                    Used by convert_bytesio_to_file_response(
                        )
                    to create proper content headers
            
            """
            file: Tuple[BytesIO, str] = await interactor(url)
            return convert_bytesio_to_file_response(
                file_source=file[1],
                stream=file[0],
            )

music_router = Router(
    route_handlers=[MusicController],
    path='/music',
    tags=['music management']
)
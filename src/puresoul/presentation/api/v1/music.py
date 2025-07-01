from io import BytesIO
from typing import Annotated, List, Callable, Optional, FrozenSet, Tuple

from fastapi import APIRouter, Depends, UploadFile, Form, HTTPException, Query, Path
from pydantic import BaseModel, ConfigDict, Field, field_validator
from starlette import status
from starlette.responses import StreamingResponse

from puresoul.application.common.dto import AlbumDTO
from puresoul.application.common.id_provider import IdProvider
from puresoul.application.common.transaction_manager import TransactionManager
from puresoul.application.create_song import CreateSongDto, SongFiles
from puresoul.application.get_feed import Feed
from puresoul.application.add_songs_to_album import AlbumSongIds
from puresoul.domain.album import Album
from puresoul.domain.genre import Genre
from puresoul.domain.song import Song
from puresoul.presentation.inmemory_file_converter import spooled_to_bytesio, convert_bytesio_to_file_response
from puresoul.presentation.interactor_factory import MainInteractorFactory


def create_music_handler(
        token_handler: Callable[[str], IdProvider],
        audio_formats: FrozenSet[str],
        image_formats: FrozenSet[str],
):
    api_router = APIRouter(
        prefix="/ams",
    )

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

    class SongSearchQuery(BaseModel):
        page: int = Field(default=1, gt=0, lt=100000000000)
        page_size: int = Field(default=15, gt=0, le=15)
        search: str = Field(
            min_length=1,
            max_length=100,
            pattern=r'^[a-zA-Z]+$'
        )
        artists: Optional[List[int]] = Field(None, min_length=1, max_length=100)
        genres: Optional[List[int]] = Field(None, min_length=1, max_length=100)

    class SongFormData(BaseModel):
        name: str
        authors: List[int]
        genres: List[int] = Field()
        description: str
        album_id: Optional[int] = Field(
            None,
            gt=0,
            description='optional album id, provided when creating a song for an album'
        )
        song: UploadFile
        cover_image: UploadFile
        model_config = ConfigDict(arbitrary_types_allowed=True)

        @field_validator(
            'genres', 'authors',
            mode='before'
        )
        def fix_list(cls, seq: list) -> List[int]:
            return [int(v) for v in seq[0].split(',')]


    def validate_file_type(file: UploadFile, allowed_types: FrozenSet[str]) -> UploadFile:
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported file type: {file.content_type}. Allowed types: {', '.join(allowed_types)}"
            )
        return file

    async def get_genres(
            ioc: Annotated[MainInteractorFactory, Depends()],
            uow: Annotated[TransactionManager, Depends()],
            id_provider: Annotated[IdProvider, Depends(token_handler)],
    ) -> List[Genre]:
        async with ioc.get_genres(uow=uow, id_provider=id_provider) as interactor:
            return await interactor()

    async def create_song(
            ioc: Annotated[MainInteractorFactory, Depends()],
            uow: Annotated[TransactionManager, Depends()],
            id_provider: Annotated[IdProvider, Depends(token_handler)],
            form_data: Annotated[SongFormData, Form(media_type='multipart/form-data')],
    ):
        validate_file_type(form_data.song, allowed_types=audio_formats)
        validate_file_type(form_data.cover_image, allowed_types=image_formats)
        create_dto = CreateSongDto(
            name=form_data.name,
            authors=form_data.authors,
            genres=form_data.genres,
            description=form_data.description,
            album_id=form_data.album_id if form_data.album_id != 0 else None,
        )
        async with ioc.create_song(uow=uow, id_provider=id_provider) as interactor:
            async with spooled_to_bytesio(form_data.song.file) as song_bytesio, spooled_to_bytesio(
                    form_data.cover_image.file) as cover_image_bytesio:
                return await interactor(
                    (
                        create_dto,
                        SongFiles(
                            song=song_bytesio,
                            cover_image=cover_image_bytesio,
                            song_filename=form_data.song.filename,
                            cover_image_filename=form_data.cover_image.filename,
                        )
                    )
                )

    async def get_song(
            id_provider: Annotated[IdProvider, Depends(token_handler)],
            interactor_factory: Annotated[MainInteractorFactory, Depends()],
            uow_factory: Annotated[TransactionManager, Depends()],
            song_id: int = Path(),
    ) -> Song:
        async with interactor_factory.get_song(id_provider=id_provider, uow=uow_factory) as interactor:
            return await interactor(song_id)


    async def search_songs(
            interactor_factory: Annotated[MainInteractorFactory, Depends()],
            uow_factory: Annotated[TransactionManager, Depends()],
            id_provider: Annotated[IdProvider, Depends(token_handler)],
            params: SongSearchQuery = Query()
    ) -> List[Song]:
        async with interactor_factory.get_feed(
                uow=uow_factory,
                id_provider=id_provider,
        ) as interactor:
            return await interactor(
                Feed(
                    page=params.page,
                    page_size=params.page_size,
                    search=params.search,
                    artists=params.artists,
                    genres=params.genres,
                )
            )

    @api_router.patch('/album/{album_id:}')
    async def publish_album(
            album_id: int,
            interactor_factory: Annotated[MainInteractorFactory, Depends()],
            uow_factory: Annotated[TransactionManager, Depends()],
            id_provider: Annotated[IdProvider, Depends(token_handler)],
    ) -> None:
        async with interactor_factory.publish_album(uow=uow_factory, id_provider=id_provider) as interactor:
            return await interactor(album_id)

    async def create_album(
                           id_provider: Annotated[IdProvider, Depends(token_handler)],
                           interactor_factory: Annotated[MainInteractorFactory, Depends()],
                           uow_factory: Annotated[TransactionManager, Depends()],
                           data: AlbumModel
    ) -> Album:
        async with interactor_factory.create_album(uow=uow_factory, id_provider=id_provider) as interactor:
            res = await interactor(
                AlbumDTO(
                    album_name=data.album_name,
                    album_description=data.album_description,
                    album_genres=data.album_genres,
                    artists=data.album_artists,
                    author_id=id_provider.get_current_user_id().id
                )
            )
            return res
    async def add_songs_to_album(
            id_provider: Annotated[IdProvider, Depends(token_handler)],
            interactor_factory: Annotated[MainInteractorFactory, Depends()],
            uow_factory: Annotated[TransactionManager, Depends()],
            song_ids: List[int] = Query(),
            album_id: int = Path(),
    ):
        async with interactor_factory.inject_song(
            id_provider=id_provider,
            uow=uow_factory,
        ) as interactor:
            res = await interactor(
                AlbumSongIds(
                    album_id=album_id,
                    song_id=song_ids,
                )
            )
            return res

    @api_router.get('/file')
    async def get_file(
            interactor_factory: Annotated[MainInteractorFactory, Depends()],
            url: str = Query(),
    ) -> StreamingResponse:
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
    
    api_router.add_api_route(
        "/genres",
        endpoint=get_genres,
        methods=["GET"],
    )
    api_router.add_api_route(
        "/albums",
        endpoint=create_album,
        methods=["POST"],
    )
    api_router.add_api_route(
        "/songs",
        endpoint=create_song,
        methods=["POST"],
    )
    api_router.add_api_route(
        '/songs/{song_id}',
        endpoint=get_song,
        methods=["GET"],
    )
    api_router.add_api_route(
        "/songs",
        endpoint=search_songs,
        methods=["GET"],
    )
    api_router.add_api_route(
        "/albums/{album_id}",
        endpoint=add_songs_to_album,
        methods=["POST"],
        status_code=status.HTTP_200_OK
    )
    return api_router

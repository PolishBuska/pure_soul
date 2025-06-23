from pathlib import Path
from typing import Annotated, List, Callable, Optional, FrozenSet

from fastapi import APIRouter, Depends, UploadFile, Form, HTTPException
from pydantic import BaseModel, ConfigDict
from pydantic import field_serializer

from puresoul.application.common.id_provider import IdProvider
from puresoul.application.common.transaction_manager import TransactionManager
from puresoul.application.create_song import CreateSongDto, SongFiles
from puresoul.domain.genre import Genre
from puresoul.presentation.inmemory_file_converter import spooled_to_bytesio
from puresoul.presentation.interactor_factory import MainInteractorFactory



def create_music_handler(
        token_handler: Callable[[str], IdProvider],
        audio_formats: FrozenSet[str],
        image_formats: FrozenSet[str],
):
    api_router = APIRouter(
        prefix="/ams",
    )

    class SongFormData(BaseModel):
        name: str
        authors: List[int]
        genres: List[int]
        description: str
        album_id: Optional[int] = 0
        song: UploadFile
        cover_image: UploadFile
        model_config = ConfigDict(arbitrary_types_allowed=True)


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


    api_router.add_api_route(
        "/genres",
        endpoint=get_genres,
        methods=["GET"],
    )
    api_router.add_api_route(
        "/songs",
        endpoint=create_song,
        methods=["POST"],
    )
    return api_router

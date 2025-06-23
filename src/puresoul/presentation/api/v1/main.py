from typing import Callable, FrozenSet

from fastapi import APIRouter

from puresoul.application.common.id_provider import IdProvider
from .oauth import create_auth_router
from .music import create_music_handler


def create_main_router(
        prefix: str,
        token_handler: Callable[[str], IdProvider],
        audio_formats: FrozenSet[str],
        image_formats: FrozenSet[str],
) -> APIRouter:
    api_router = APIRouter(
        prefix=prefix,
    )
    api_router.include_router(
        create_auth_router(), tags=["auth"]
    )
    api_router.include_router(
        create_music_handler(
            token_handler=token_handler,
            audio_formats=audio_formats,
            image_formats=image_formats,
        ), tags=["music"])
    return api_router

from typing import List

from src.application.common.file_storage import FileStorage
from src.application.common.id_provider import IdProvider
from src.application.common.music_gateway import MusicGateway
from src.application.common.names_hasher import NamesHasher
from src.application.common.transaction_manager import TransactionManager
from src.application.common.user_gateway import UserGateway
from src.domain.exceptions import NotAuthorizedException
from src.domain.playlist import PlaylistService


class PlaylistDTO:
    playlist_name: str
    playlist_description: str
    playlist_genres: List[int]
    playlist_songs: List[int]


async def create_playlist(
        dto: PlaylistDTO,
        file_storage: FileStorage,
        music_gateway: MusicGateway,
        transaction_manager: TransactionManager,
        id_provider: IdProvider,
        user_gateway: UserGateway,
):
    current_user = id_provider.get_current_user_id()
    if not current_user.can_access_premium_features():
        raise NotAuthorizedException(
            f'user {current_user.username} is not authorized to access premium features'
        )

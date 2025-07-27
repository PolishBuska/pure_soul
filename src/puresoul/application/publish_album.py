from .common.id_provider import IdProvider
from .common.interactor import Interactor
from .common.music_gateway import MusicGateway
from puresoul.domain.exceptions import (
    NotAuthorizedException,
    TooFewItemsException,
    AlreadyPublic, NotFound,

)
from .common.transaction_manager import TransactionManager

class PublishAlbum(Interactor[int, None]):
    def __init__(
            self,
            music_gateway: MusicGateway,
            id_provider: IdProvider,
            transaction_manager: TransactionManager,
    ):
        self.music_gateway = music_gateway
        self.id_provider = id_provider
        self.transaction_manager = transaction_manager

    async def __call__(self, album_id: int) -> None:
        current_user = self.id_provider.get_current_user_id()
        if not current_user.can_access_premium_features():
            raise NotAuthorizedException(
                "cannot access this feature"
            )
        album = await self.music_gateway.get_album_by_id(album_id)
        if album is None:
            raise NotFound(
                f"could not find album with id {album_id}"
            )
        album.publish_album(
            cu=current_user
        )
        await self.music_gateway.update_album(album)
        await self.transaction_manager.commit()

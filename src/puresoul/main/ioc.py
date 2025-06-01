from contextlib import asynccontextmanager
from typing import Self, Any

from sqlalchemy.ext.asyncio import AsyncSession

from puresoul.adapters.gateways.sqla.music_gateway import SqlaMusicGateway
from puresoul.adapters.gateways.sqla.payment_gateway import SaPaymentGateway
from puresoul.adapters.gateways.sqla.subscription_gateway import SQLASubscriptionGateway
from puresoul.adapters.gateways.sqla.tier_gateway import SQLATierGateway
from puresoul.adapters.gateways.sqla.user_gateway import SqlaUserGateway
from puresoul.application.add_subscription import AddSubscription
from puresoul.application.check_subscription import CheckSubscription
from puresoul.application.common.file_storage import FileStorage
from puresoul.application.common.id_provider import IdProvider
from puresoul.application.common.names_hasher import NamesHasher
from puresoul.application.common.password_hasher import PasswordHasher
from puresoul.application.common.payment_provider import PaymentProvider
from puresoul.application.common.token_generator import TokenGenerator
from puresoul.application.common.transaction_manager import TransactionManager
from puresoul.application.create_artist import CreateArtist
from puresoul.application.create_song import CreateSong
from puresoul.application.create_user import CreateUser
from puresoul.application.find_artists_by_names import FindArtistsByNames
from puresoul.application.get_feed import GetFeed
from puresoul.application.get_genres import GetGenres
from puresoul.application.get_payment_types import GetPaymentTypes
from puresoul.application.get_song import GetSong
from puresoul.application.get_tiers import GetTiers
from puresoul.application.login_user import LoginUser
from puresoul.application.download_presigned_url import DownloadPresignedUrl
from puresoul.domain.artist import ArtistService
from puresoul.domain.iam.user import UserService
from puresoul.domain.song import SongService
from puresoul.domain.subscription.model import SubscriptionService
from puresoul.presentation.interactor_factory import UserInteractorFactory


class WebIoc(UserInteractorFactory):
    def __init__(
            self,
            user_service: UserService,
            password_hasher: PasswordHasher,
            art_service: ArtistService,
            song_file_storage: FileStorage,
            song_service: SongService,
            names_hasher: NamesHasher,
            token_generator: TokenGenerator,
            payment_provider: PaymentProvider,
            subscription_service: SubscriptionService,
            image_file_storage: FileStorage,
    ):
        self.user_service = user_service
        self.password_hasher = password_hasher
        self.art_service = art_service
        self.file_storage = song_file_storage
        self.song_service = song_service
        self.names_hasher = names_hasher
        self.token_generator = token_generator
        self.payment_provider = payment_provider
        self.subscription_service = subscription_service
        self.image_file_storage = image_file_storage

    @asynccontextmanager
    async def create_user(
            self,
            uow: TransactionManager | AsyncSession,
    ) -> CreateUser:
        yield CreateUser(
            transaction_manager=uow,
            user_gateway=SqlaUserGateway(
                uow=uow
            ),
            user_service=self.user_service,
            password_hasher=self.password_hasher,
        )
    @asynccontextmanager
    async def create_artist(
            self,
            uow,
            id_provider: IdProvider,
    ) -> CreateArtist:
        yield CreateArtist(
            transaction_manager=uow,
            user_gateway=SqlaUserGateway(uow=uow),
            id_provider=id_provider,
            artist_service=self.art_service,
        )

    @asynccontextmanager
    async def create_song(
            self,
            uow,
            id_provider: IdProvider,
    ) -> CreateSong:
        yield CreateSong(
            song_file_storage=self.file_storage,
            transaction_manager=uow,
            id_provider=id_provider,
            song_service=self.song_service,
            music_gateway=SqlaMusicGateway(uow),
            user_gateway=SqlaUserGateway(uow),
            names_hasher=self.names_hasher,
            image_file_storage=self.image_file_storage
        )
    @asynccontextmanager
    async def get_genres(
            self,
            uow,
            id_provider: IdProvider,
    ) -> GetGenres:
        yield GetGenres(
            music_gateway=SqlaMusicGateway(uow=uow),
            id_provider=id_provider,
        )
    @asynccontextmanager
    async def login_user(
            self,
            uow
    ) -> LoginUser:
        yield LoginUser(
            user_gateway=SqlaUserGateway(uow=uow),
            password_hasher=self.password_hasher,
            token_generator=self.token_generator
        )

    @asynccontextmanager
    async def add_subscription(self, uow, id_provider: IdProvider) -> AddSubscription:
        yield AddSubscription(
            user_gateway=SqlaUserGateway(uow=uow),
            transaction_manager=uow,
            user_service=self.user_service,
            payment_provider=self.payment_provider,
            id_provider=id_provider,
            tiers_gateway=SQLATierGateway(uow=uow),
            subscription_gateway=SQLASubscriptionGateway(uow=uow),
            subscription_service=self.subscription_service,
            payment_gateway=SaPaymentGateway(uow=uow),
        )
    @asynccontextmanager
    async def get_tiers(self, uow: Any) -> GetTiers:
        yield GetTiers(
            tiers_gateway=SQLATierGateway(uow=uow),
        )
    @asynccontextmanager
    async def check_subscription(self, uow: Any, id_provider: IdProvider) -> CheckSubscription:
        yield CheckSubscription(
            subscription_gateway=SQLASubscriptionGateway(uow=uow),
            id_provider=id_provider,
        )

    @asynccontextmanager
    async def get_payments_types(self, uow, id_provider: IdProvider) -> GetPaymentTypes:
        yield GetPaymentTypes(
            payment_gateway=SaPaymentGateway(uow=uow),
        )

    @asynccontextmanager
    async def find_artists_by_names(self, uow) -> FindArtistsByNames:
        yield FindArtistsByNames(
            user_gateway=SqlaUserGateway(uow=uow),
        )

    @asynccontextmanager
    async def get_song(self, uow, id_provider: IdProvider):
        yield GetSong(
            song_file_storage=self.file_storage,
            id_provider=id_provider,
            image_file_storage=self.image_file_storage,
            music_gateway=SqlaMusicGateway(uow),
            transaction_manager=uow
        )

    @asynccontextmanager
    async def get_file(self):
        yield DownloadPresignedUrl(
            file_storage=self.file_storage,
        )

    @asynccontextmanager
    async def get_feed(self, uow, id_provider: IdProvider):
        yield GetFeed(
            song_file_storage=self.file_storage,
            music_gateway=SqlaMusicGateway(uow),
            transaction_manager=uow,
            id_provider=id_provider,
            image_file_storage=self.image_file_storage,
        )

    async def __call__(self) -> Self:
        return self

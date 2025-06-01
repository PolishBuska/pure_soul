from typing import List, Optional, NewType

from dataclasses import dataclass, field, asdict

from .exceptions import NotOldEnoughException
from .constants import Grants
from ..subscription.constants import SubscriptionStatus
from ..types import UserId, UserName, EmailAddress


@dataclass(eq=True, unsafe_hash=True, frozen=False)
class BaseUser:
    id: Optional[UserId] = field(hash=False)
    username: UserName = field(hash=True)
    email: EmailAddress = field(hash=True)
    grants: List[Optional[Grants]] = field(hash=False)
    is_adult: bool = field(hash=False)
    subscription_id: int = field(hash=False)
    password: Optional[str] = field(hash=False)

    def as_dict(self) -> dict:
        return asdict(self)

    def can_listen(self) -> bool:
        if Grants.CAN_LISTEN.value not in self.grants:
            return False
        return True

    def can_create_playlist(self) -> bool:
        if Grants.CAN_CREATE_PLAYLIST.value not in self.grants:
            return False
        return True

    def can_download_songs(self) -> bool:
        if Grants.CAN_DOWNLOAD_SONGS.value not in self.grants:
            return False
        return True

    def can_skip_ads(self) -> bool:
        if Grants.CAN_SKIP_ADS.value not in self.grants:
            return False
        return True

    def can_access_premium_features(self) -> bool:
        if Grants.CAN_ACCESS_PREMIUM_FEATURES.value not in self.grants:
            return False
        return True

class UserService:
    def create_user(self, age: int, username: str, email: str, password: str) -> BaseUser:
        if age < 16:
            raise NotOldEnoughException(
                f"User with the name:{username} cannot be created with age {age}. Too young"
            )
        if age > 150:
            raise NotOldEnoughException(
                f"User with the name:{username} cannot be created with age {age}. Invalid"
            )
        return BaseUser(
            username=UserName(username),
            email=EmailAddress(email),
            is_adult=True if age >= 18 else False,
            id=None,
            grants=[Grants.CAN_LISTEN],
            password=password,
            subscription_id=SubscriptionStatus.FREE.value
        )

from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal

from .constants import SubscriptionStatus


@dataclass
class SubscriptionTier:
    id: int
    name: str
    price: Decimal
    ending_threshold: timedelta

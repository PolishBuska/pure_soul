from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class ActiveSubscription:
    id: Optional[int]
    started_at: datetime
    ended_at: datetime
    tier_id: int
    user_id: int
    payment_id: str
    payment_method: int

class SubscriptionService:
    def create_subscription(
            self,
            ending_threshold: timedelta,
            tier_id: int,
            user_id: int,
            payment_id: str,
            payment_method: int,
    ) -> ActiveSubscription:
        starting_datetime = datetime.now()
        return ActiveSubscription(
            id=None,
            started_at=starting_datetime,
            ended_at=starting_datetime + ending_threshold,
            tier_id=tier_id,
            user_id=user_id,
            payment_id=payment_id,
            payment_method=payment_method,
        )

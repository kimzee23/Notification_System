import datetime
from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from domain.entities.delivery_attempt import DeliveryAttempt


class Channel(str, Enum):
    PUSH = "push"
    SMS = "sms"
    EMAIL = "email"

class NotificationStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    DELIVERED = 'delivered'
    FAILED = "failed"
    CANCELED = "canceled"

@dataclass
class Notification:
    id: UUID
    idempotency: str
    user_id: str
    channel: Channel
    payload: dict
    priority: int
    status: NotificationStatus
    attempts: list
    created_at: datetime
    scheduled_at: datetime


    def mark_delivered(self, provider: str) -> None:
        self.status = NotificationStatus.DELIVERED
        self.attempts.append(DeliveryAttempt(provider=provider, success=True))


    def mark_failed(self, provider: str, reason: str) -> None:
        self.attempts.append(DeliveryAttempt(provider=provider, success=False, reason=reason))
        if len(self.attempts) >= 3:
            self.status = NotificationStatus.FAILED


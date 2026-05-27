from uuid import UUID

from pydantic.dataclasses import dataclass


@dataclass
class NotificationDelivered:
    notification_id: UUID

@dataclass
class NotificationFailed:
    notification_id: UUID
    error_message: str
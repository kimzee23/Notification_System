from dataclasses import dataclass
from uuid import UUID


@dataclass
class NotificationResult:
    notification_id: UUID | None = None
    success: bool = False
    duplicate: bool = False

    @classmethod
    def duplicate(cls, key: str):
        return cls(
            notification_id=key,
            success=False,
            duplicate=True
        )
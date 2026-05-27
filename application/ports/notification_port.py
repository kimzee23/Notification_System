from abc import ABC, abstractmethod

from pydantic.dataclasses import dataclass

from domain.entities.notification import Notification, Channel


@dataclass
class DeliveryResult:
    success: bool
    provider_id : str
    error_message : str
    retryable: bool

class NotificationPort(ABC):
    # "Outbound port — adapters implement this, domain depends on it."
    @abstractmethod
    async def send (self, notification: Notification) -> DeliveryResult: ...
    @abstractmethod
    def supports_channel(self,channel : Channel) -> bool: ...
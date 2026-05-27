from google.oauth2.gdch_credentials import ServiceAccountCredentials

from firebase_admin.messaging import (
    Message,
    Notification as FCMNotification
)

from application.services.circuit_breaker import (
    CircuitBreaker,
    ProviderUnavailableError
)

from application.ports.notification_port import (
    NotificationPort,
    DeliveryResult
)

from domain.entities.notification import (
    Notification,
    Channel
)

class FCMAdapter(NotificationPort):
    def __init__(self, credentials: ServiceAccountCredentials,
                 circuit_breaker: CircuitBreaker): ...

    def supports_channel(self, channel: Channel) -> bool:
        return channel == Channel.PUSH

    async def send(self, notification: Notification) -> DeliveryResult:
        message = Message(
            notification=FCMNotification(
                title=notification.payload['title'],
                body=notification.payload['body'],
            ),
            token=notification.payload['device_token'],
        )
        try:
            response = await self.circuit_breaker.call(
                self._fcm_client.send_async, message
            )
            return DeliveryResult(success=True, provider_id=response)
        except ProviderUnavailableError:
            return DeliveryResult(success=False, error_message='circuit_open', retryable=False)
        except Exception as e:
            return DeliveryResult(success=False, error_message=str(e), retryable=True)



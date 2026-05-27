from domain.entities.notification import Notification


class SendNotification:
    def __init__(
            self,idempotency_svc,channel_router,saga,repo, event_bus):
        self.idempotency_svc = idempotency_svc
        self.channel_router = channel_router
        self.saga = saga
        self.repo = repo
        self.event_bus = event_bus

    async def execute(self, cmd):
        # Idempotency check
        if await self.idempotency_svc.already_processed(
                cmd.idempotency_key
        ):
            return NotificationResult.duplicate(
                cmd.idempotency_key
            )
        notification = Notification(
            idempotency=cmd.idempotency_key,
            user_id=cmd.user_id,
            channel=cmd.channel,
            payload=cmd.payload,
            priority=cmd.priority
        )
        await self.repo.save(notification)

        adapter = self.channel_router.resolve(notification)
        result  = await self.saga.run(notification, adapter)
        if result.success:
            event = NotificationDelivered(notification.id)
        else:
            event = NotificationFailed(
                notification.id,
                result.error_message
            )

        await self.event_bus.publish(event)

        return NotificationResult(
            notification_id=notification.id,
            success=result.success
        )


from domain.entities.notification import Notification


class SendNotification:
    def __init__(self, idempotency_svc, channel_router,saga, repo, event_bus): ...

    async def execute(self, cmd: SendNotificationCommand) -> NotificationResult:
        # 1. Idempotency guard
        if await self.idempotency_svc.already_processed(cmd.idempotency_key):
            return NotificationResult.duplicate(cmd.idempotency_key)


        notification = Notification(
            cmd.idempotency_key=cmd.idempotency_key, user_id=cmd.user_id,channel=cmd.channel,
            payload=cmd.payload,
            priority=cmd.priority,)
        await self.repo.save(notification)

        adapter = self.channel_router.resolve(notification)
        result  = await self.saga.run(notification, adapter)

        # 4. Publish event
        event = NotificationDelivered(notification.id) if result.success \
                else NotificationFailed(notification.id, result.error)
        await self.event_bus.publish(event)

        return NotificationResult(notification_id=notification.id, success=result.success=result.success)




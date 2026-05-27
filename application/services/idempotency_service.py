from redis.asyncio import Redis

from domain.entities.notification import Notification
IDEMPOTENCY_TTL_SECONDS = 3600

class IdempotencyService:
    def __init__(self, redis: Redis):
        self.redis = redis
    async def already_processed(self,key:str) -> bool:
        """
        Returns true if request is duplicate
        Uses atomic Redis SET NX EX.
        """
        result = await self.redis.set(
            f"idem:{key}",
            "1",
            nx=True,
            ex=IDEMPOTENCY_TTL_SECONDS

        )
        return result is None
    async def get_idem(self,key:str) -> None:
        """
        Optional cleanup for failed workflow
        """
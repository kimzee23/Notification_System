from enum import Enum
from typing import Callable , Any
from redis.asyncio import Redis

class CircuitBreaker(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class ProviderUnavailableError(Exception):
    pass

class CircuitState:

    def __init__(
            self,
            provider: str,
            redis: Redis,
            failure_threshold: int = 5,
            recovery_timeout: int = 60
    ):
        self.provider = provider
        self.redis = redis
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

    async def call(self, fn: Callable, *args) -> Any:

        state = await self._get_state()

        if state == CircuitState.OPEN:
            raise ProviderUnavailableError(self.provider)

        try:
            result = await fn(*args)

            await self._on_success()

            return result

        except Exception:
            await self._on_failure()
            raise

    async def _get_state(self) -> CircuitState:

        value = await self.redis.get(
            f"cb:{self.provider}:state"
        )

        if value is None:
            return CircuitState.CLOSED

        return CircuitState(value.decode())

    async def _on_success(self):

        await self.redis.delete(
            f"cb:{self.provider}:failures"
        )

        await self.redis.set(
            f"cb:{self.provider}:state",
            CircuitState.CLOSED.value
        )

    async def _on_failure(self):

        count = await self.redis.incr(
            f"cb:{self.provider}:failures"
        )

        await self.redis.expire(
            f"cb:{self.provider}:failures",60
        )

        if count >= self.failure_threshold:

            await self.redis.set(
                f"cb:{self.provider}:state", CircuitState.OPEN.value,
                ex=self.recovery_timeout
            )
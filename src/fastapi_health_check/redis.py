from __future__ import annotations

from typing import Protocol

from fastapi_health_check.checks import HealthCheck


class RedisClient(Protocol):
    async def ping(self) -> object: ...


class RedisCheck(HealthCheck):
    default_name = "redis"

    def __init__(self, client: RedisClient, name: str | None = None) -> None:
        super().__init__(name=name)
        self._client = client

    async def check(self) -> str:
        await self._client.ping()
        return "Redis available"

from __future__ import annotations

import asyncio

from fastapi_health_check import RedisCheck


class AvailableRedisClient:
    def __init__(self) -> None:
        self.ping_requested = False

    async def ping(self) -> bool:
        self.ping_requested = True
        return True


def test_redis_check_reuses_async_client_and_pings_server() -> None:
    client = AvailableRedisClient()

    result = asyncio.run(RedisCheck(client, name="session_cache").run())

    assert result.name == "session_cache"
    assert result.status == "ok"
    assert result.message == "Redis available"
    assert client.ping_requested is True

from __future__ import annotations

import asyncio

from fastapi_health_check import RedisCheck


class AvailableRedisClient:
    def __init__(self) -> None:
        self.ping_requested = False

    async def ping(self) -> bool:
        self.ping_requested = True
        return True


class UnavailableRedisClient:
    async def ping(self) -> bool:
        raise ConnectionError("could not connect to redis://default:secret@redis.internal:6379/0")


def test_redis_check_reuses_async_client_and_pings_server() -> None:
    client = AvailableRedisClient()

    result = asyncio.run(RedisCheck(client, name="session_cache").run())

    assert result.name == "session_cache"
    assert result.status == "ok"
    assert result.message == "Redis available"
    assert client.ping_requested is True


def test_redis_check_sanitizes_connection_failures() -> None:
    result = asyncio.run(RedisCheck(UnavailableRedisClient()).run())

    assert result.status == "fail"
    assert result.message == "Redis unavailable"
    assert "default" not in result.model_dump_json()
    assert "secret" not in result.model_dump_json()
    assert "redis.internal" not in result.model_dump_json()

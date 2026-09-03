# Custom Checks

## Built-in Redis check

`RedisCheck` verifies connectivity with `PING` through an existing async client. Reusing the application client and its connection pool avoids creating a new connection for every health request.

The Redis client is optional and is not installed with the core package. Install a compatible async client such as `redis` in the application.

```python
from redis.asyncio import Redis

from fastapi_health_check import HealthRegistry, RedisCheck


redis_client = Redis.from_url(redis_url)
registry = HealthRegistry([RedisCheck(redis_client)])
```

The client must provide an async `ping()` method. A custom name is supported:

```python
registry.register(RedisCheck(session_redis, name="session_cache"))
```

A successful check reports `Redis available`. A connection failure reports `Redis unavailable` without including the original client message, preventing credentials from leaking through health responses.

As with every current health check, a Redis failure is critical and makes its health report fail.

## Function-based checks

The easiest way to monitor custom areas is `health_check()`.

### Synchronous checks

```python
from fastapi_health_check import health_check

database_check = health_check("database", lambda: "connection ok")
redis_check = health_check("redis", lambda: "cache reachable")
```

### Asynchronous checks

```python
from fastapi_health_check import health_check


async def payments_api_check() -> str | None:
    return "payments API available"


payments_check = health_check("payments_api", payments_api_check)
```

## Class-based checks

Use class-based checks when you need more structure.

```python
from fastapi_health_check import HealthCheck


class QueueCheck(HealthCheck):
    default_name = "queue"

    async def check(self) -> str | None:
        return "queue connected"
```

Class-based checks are useful for:

- dependency injection through `__init__`
- reusable state
- richer custom behavior
- wrapping service clients cleanly

## Example areas to monitor

- database connectivity
- Redis availability
- queue backends
- object storage
- third-party APIs
- feature-specific internal services

# Custom Checks

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

# Custom Checks

## Built-in PostgreSQL check

`PostgreSQLCheck` verifies connectivity with `SELECT 1` through an existing async pool. Reusing the application pool avoids opening a new database connection for every health request.

The PostgreSQL driver is optional and is not installed with the core package. Install a compatible async driver such as `asyncpg` in the application.

```python
import asyncpg

from fastapi_health_check import HealthRegistry, PostgreSQLCheck


pool = await asyncpg.create_pool(database_url)
registry = HealthRegistry([PostgreSQLCheck(pool)])
```

The pool must provide an async `acquire()` context manager whose connection supports `execute()`. A custom name is supported:

```python
registry.register(PostgreSQLCheck(reporting_pool, name="reporting_database"))
```

A successful check reports `PostgreSQL available`. A connection or query failure reports `PostgreSQL unavailable` without including the original driver message, preventing credentials from leaking through health responses.

As with every current health check, a PostgreSQL failure is critical and makes its health report fail.

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

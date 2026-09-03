# Custom Checks

## Built-in SQLAlchemy check

`SQLAlchemyCheck` verifies database connectivity with `SELECT 1` through the same engine or session factory used by the application.

Install the optional integration with `uv`:

```bash
uv add "fastapi-ht[sqlalchemy]"
```

Or with `pip`:

```bash
pip install "fastapi-ht[sqlalchemy]"
```

The integration supports SQLAlchemy `>=2.0,<3.0` and these modern SQLAlchemy APIs:

- `sqlalchemy.Engine`
- `sqlalchemy.ext.asyncio.AsyncEngine`
- `sqlalchemy.orm.sessionmaker`
- `sqlalchemy.ext.asyncio.async_sessionmaker`

An existing async engine can be registered directly:

```python
from sqlalchemy.ext.asyncio import create_async_engine

from fastapi_health_check import HealthRegistry, SQLAlchemyCheck


engine = create_async_engine(database_url)
registry = HealthRegistry([SQLAlchemyCheck(engine)])
```

Session factories are also supported:

```python
from sqlalchemy.ext.asyncio import async_sessionmaker


sessions = async_sessionmaker(engine)
registry.register(SQLAlchemyCheck(sessions, name="primary_database"))
```

Both synchronous and asynchronous engines and session factories execute the same lightweight query. Synchronous operations run in a worker thread and do not block the FastAPI event loop.

SQLAlchemy is not installed with the core package. Applications that do not install the `sqlalchemy` extra do not receive SQLAlchemy or its async support dependencies.

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

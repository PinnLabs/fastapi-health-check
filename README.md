<p align="center">
    <img src="https://raw.githubusercontent.com/PinnLabs/fastapi-health-check/main/public/logo.png" alt="fastapi-health-check logo" width="520" style="display: block; margin:
    0 auto;" />
</p>

# fastapi-health-check

FastAPI health checks with separate liveness and readiness probes, a visual status page, and JSON responses.

### Example interface

![fastapi-health-check example interface](https://raw.githubusercontent.com/PinnLabs/fastapi-health-check/main/public/example_use.png)

## Installation

Install with `uv`:

```bash
uv add fastapi-ht
```

Install with `pip`:

```bash
pip install fastapi-ht
```

## What the library provides

- A base contract for advanced checks
- A lightweight registry for collecting and running checks
- Separate `/health/live` and `/health/ready` JSON endpoints
- A combined `/ht` endpoint with HTML by default
- JSON responses when the client sends `Accept: application/json`
- A simple way to monitor any custom area of your system

## Built-in checks

The package includes `AppAliveCheck` for application availability and `RedisCheck` for Redis connectivity.

`RedisCheck` reuses an async client supplied by the application and executes `PING`. The core package does not install a Redis client. Install and configure an async client such as `redis` in the application when this check is needed.

```python
from redis.asyncio import Redis

from fastapi_health_check import HealthRegistry, RedisCheck


redis_client = Redis.from_url(redis_url)
registry = HealthRegistry([RedisCheck(redis_client)])
```

The default check name is `redis`. A custom name can distinguish multiple Redis deployments:

```python
registry.register(RedisCheck(session_redis, name="session_cache"))
```

Redis failures are critical like every health check currently registered in `HealthRegistry`. Connection errors use a sanitized message and never expose credentials from the underlying client exception.

Databases, queues, external APIs, or any other monitored area are meant to be registered by the user.
The package includes `AppAliveCheck` for application availability and `PostgreSQLCheck` for PostgreSQL connectivity.

`PostgreSQLCheck` reuses an async pool supplied by the application and executes `SELECT 1`. The core package does not install a PostgreSQL driver. Install and configure an async driver such as `asyncpg` in the application when this check is needed.

```python
import asyncpg

from fastapi_health_check import HealthRegistry, PostgreSQLCheck


pool = await asyncpg.create_pool(database_url)
registry = HealthRegistry([PostgreSQLCheck(pool)])
```

The default check name is `postgresql`. A custom name can distinguish multiple databases:

```python
registry.register(PostgreSQLCheck(reporting_pool, name="reporting_database"))
```

PostgreSQL failures are critical like every health check currently registered in `HealthRegistry`. Connection errors use a sanitized message and never expose credentials from the underlying driver exception.

Redis, queues, external APIs, or any other monitored area are meant to be registered by the user.

## Quick start

```python
from fastapi import FastAPI

from fastapi_health_check import AppAliveCheck, HealthRegistry, health_check, install_health_check


app = FastAPI()
registry = HealthRegistry()
registry.register(AppAliveCheck(), readiness=True, liveness=True)
registry.register(health_check("database", lambda: "connection ok"))
registry.register(health_check("redis", lambda: "cache reachable"))

install_health_check(app, registry)
```

This exposes three routes:

- `GET /health/live` returns the liveness report as JSON
- `GET /health/ready` returns the readiness report as JSON
- `GET /ht` keeps the combined status page and content-negotiated JSON response

## Liveness and readiness

Liveness answers whether the application process should be restarted. Keep this probe lightweight and independent of databases, caches, external APIs, and other dependencies. A failing liveness check returns `503`.

Readiness answers whether the application can serve traffic. Dependency checks belong here so an unavailable dependency returns `503` and the orchestrator can remove the instance from service without restarting it.

Checks belong to readiness by default:

```python
registry.register(health_check("database", check_database))
```

Assign a check to liveness or both probes with registration options:

```python
registry.register(process_check, readiness=False, liveness=True)
registry.register(AppAliveCheck(), readiness=True, liveness=True)
```

Probe paths can be configured independently while retaining `/ht`:

```python
install_health_check(
    app,
    registry,
    path="/status",
    liveness_path="/livez",
    readiness_path="/readyz",
)
```

For Kubernetes, configure `livenessProbe` to request `/health/live` and `readinessProbe` to request `/health/ready`. Dependency failures then stop traffic to an unready pod without creating unnecessary restart loops. Kubernetes manifest settings are deployment-specific and outside this library's configuration.

## Monitoring custom areas

If you want to monitor anything beyond the built-in app liveness check, the easiest option is the `health_check()` factory.

You can use it for:

- databases
- Redis or cache layers
- background queues
- external APIs
- storage services
- internal domain-specific dependencies

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

### Class-based checks for advanced cases

```python
from fastapi_health_check import HealthCheck


class QueueCheck(HealthCheck):
    default_name = "queue"

    async def check(self) -> str | None:
        return "queue connected"
```

Use class-based checks when you want:

- dependency injection through `__init__`
- reusable state
- more structured custom behavior

## Local manual testing

The repository includes a local example application at `src/examples/basic_app.py`.

Run it with:

```bash
uv run uvicorn src.examples.basic_app:app --reload
```

Then open:

- `http://127.0.0.1:8000/ht` for the HTML page
- `curl -H "Accept: application/json" http://127.0.0.1:8000/ht` for JSON
- `curl http://127.0.0.1:8000/health/live` for liveness
- `curl http://127.0.0.1:8000/health/ready` for readiness

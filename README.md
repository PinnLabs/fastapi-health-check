<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/PinnLabs/fastapi-health-check/main/public/logo-dark.png">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/PinnLabs/fastapi-health-check/main/public/logo-light.png">
    <img alt="fastapi-health-check logo" src="https://raw.githubusercontent.com/PinnLabs/fastapi-health-check/main/public/logo-light.png" width="220">
  </picture>
</p>

<h1 align="center">fastapi-health-check</h1>

<p align="center">
  FastAPI health checks with separate liveness and readiness probes, a visual status page, and JSON responses.
</p>

<p align="center">
  <a href="https://pypi.org/project/fastapi-ht/"><img alt="PyPI" src="https://img.shields.io/pypi/v/fastapi-ht?color=0b7285&label=pypi"></a>
  <a href="https://pypi.org/project/fastapi-ht/"><img alt="Python versions" src="https://img.shields.io/pypi/pyversions/fastapi-ht"></a>
  <a href="https://github.com/PinnLabs/fastapi-health-check/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/PinnLabs/fastapi-health-check/actions/workflows/ci.yml/badge.svg"></a>
  <a href="https://pinnlabs.github.io/fastapi-health-check/"><img alt="Docs" src="https://img.shields.io/badge/docs-mkdocs--material-0b7285"></a>
</p>

<p align="center">
  <a href="https://pinnlabs.github.io/fastapi-health-check/">Documentation</a>
  &nbsp;&middot;&nbsp;
  <a href="#installation">Installation</a>
  &nbsp;&middot;&nbsp;
  <a href="#what-the-library-provides">Features</a>
  &nbsp;&middot;&nbsp;
  <a href="https://github.com/PinnLabs/fastapi-health-check/issues">Issues</a>
</p>

---

<p align="center">
  <img alt="The /ht status page of the enterprise example: 14 dependency checks, all healthy" src="https://raw.githubusercontent.com/PinnLabs/fastapi-health-check/main/public/example_use.png" width="900">
</p>

<p align="center">
  <sub>The built-in <code>/ht</code> status page — every registered check with its status, message and duration.</sub>
</p>

When a dependency goes down, the failing check is highlighted, the overall status flips and `/ht` answers `503`:

<p align="center">
  <img alt="The same status page with the payments_api check failing and the overall status reporting issues" src="https://raw.githubusercontent.com/PinnLabs/fastapi-health-check/main/public/example_failure.png" width="900">
</p>

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

### SQLAlchemy

Install the optional SQLAlchemy support:

```bash
uv add "fastapi-ht[sqlalchemy]"
```

`SQLAlchemyCheck` supports SQLAlchemy `>=2.0,<3.0` and accepts an existing `Engine`, `AsyncEngine`, `sessionmaker`, or `async_sessionmaker`.

```python
from sqlalchemy.ext.asyncio import create_async_engine

from fastapi_health_check import HealthRegistry, SQLAlchemyCheck


engine = create_async_engine(database_url)
registry = HealthRegistry([SQLAlchemyCheck(engine)])
```

The check executes `SELECT 1` through the supplied engine or session factory. Synchronous SQLAlchemy operations run in a worker thread so health checks do not block the application event loop.

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

A larger example lives at `src/examples/enterprise_app.py`. It registers 14 dependency
checks and exposes a small console that can fail, slow down or recover each one, which
is what the screenshots above show:

```bash
uv run uvicorn src.examples.enterprise_app:app --reload
```

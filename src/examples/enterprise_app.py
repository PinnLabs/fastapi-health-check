"""Large-application example for fastapi-health-check.

Simulates the dependency surface of a production e-commerce platform:
a real SQLite database checked through SQLAlchemy plus simulated caches,
queues, storage, search, and third-party APIs.

Run it with:

    uv run uvicorn src.examples.enterprise_app:app --reload

Then open http://127.0.0.1:8000/ and use the demo controls to break and
recover dependencies while watching /ht, /health/live and /health/ready.
"""

from __future__ import annotations

import asyncio
import random
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from fastapi_health_check import (
    AppAliveCheck,
    HealthCheck,
    HealthRegistry,
    SQLAlchemyCheck,
    health_check,
    install_health_check,
)

DATABASE_URL = "sqlite+aiosqlite:///./enterprise_demo.db"

engine = create_async_engine(DATABASE_URL, future=True)
session_factory = async_sessionmaker(engine, expire_on_commit=False)


class DependencySimulator:
    """In-memory switchboard used to fail or recover simulated dependencies."""

    def __init__(self) -> None:
        self._down: set[str] = set()
        self._slow: set[str] = set()

    def fail(self, name: str) -> None:
        self._down.add(name)

    def slow(self, name: str) -> None:
        self._slow.add(name)

    def recover(self, name: str) -> None:
        self._down.discard(name)
        self._slow.discard(name)

    def recover_all(self) -> None:
        self._down.clear()
        self._slow.clear()

    def is_down(self, name: str) -> bool:
        return name in self._down

    def is_slow(self, name: str) -> bool:
        return name in self._slow

    def state(self, name: str) -> str:
        if name in self._down:
            return "down"
        if name in self._slow:
            return "slow"
        return "up"


simulator = DependencySimulator()


async def simulate_latency(name: str, base_ms: int) -> None:
    jitter = random.uniform(0.5, 1.5)
    latency = base_ms * (12 if simulator.is_slow(name) else 1) * jitter
    await asyncio.sleep(latency / 1000)


class SimulatedDependencyCheck(HealthCheck):
    """Class-based check with dependency injection and a latency profile."""

    def __init__(self, name: str, *, base_latency_ms: int, success_message: str, failure_message: str) -> None:
        super().__init__(name=name)
        self._base_latency_ms = base_latency_ms
        self._success_message = success_message
        self._failure_message = failure_message

    async def check(self) -> str | None:
        await simulate_latency(self.name, self._base_latency_ms)

        if simulator.is_down(self.name):
            raise ConnectionError(self._failure_message)

        if simulator.is_slow(self.name):
            return f"{self._success_message} (degraded latency)"

        return self._success_message


async def database_migrations_check() -> str:
    """Real query against the demo database through the session factory."""
    async with session_factory() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM schema_migrations"))
        applied = result.scalar_one()

    if simulator.is_down("database_migrations"):
        raise RuntimeError("pending migrations detected")

    return f"{applied} migrations applied"


def worker_pool_check() -> str:
    """Synchronous check: FunctionHealthCheck runs it in a worker thread."""
    if simulator.is_down("worker_pool"):
        raise RuntimeError("no worker heartbeat in the last 60s")

    return "8/8 workers heartbeating"


async def feature_flags_check() -> str:
    await simulate_latency("feature_flags", 15)
    if simulator.is_down("feature_flags"):
        raise ConnectionError("feature flag provider unreachable, falling back to defaults")
    return "flag snapshot fresh"


registry = HealthRegistry()

# --- Liveness: process-level only, no dependencies ---------------------------
registry.register(AppAliveCheck(), readiness=True, liveness=True)
registry.register(
    SimulatedDependencyCheck(
        "event_loop",
        base_latency_ms=1,
        success_message="event loop responsive",
        failure_message="event loop blocked",
    ),
    readiness=False,
    liveness=True,
)

# --- Readiness: every dependency required to serve traffic -------------------
registry.register(SQLAlchemyCheck(session_factory, name="postgresql_primary"))
registry.register(health_check("database_migrations", database_migrations_check))
registry.register(
    SimulatedDependencyCheck(
        "redis_sessions",
        base_latency_ms=8,
        success_message="session cache reachable",
        failure_message="redis connection refused",
    )
)
registry.register(
    SimulatedDependencyCheck(
        "redis_ratelimit",
        base_latency_ms=8,
        success_message="rate limit cache reachable",
        failure_message="redis connection refused",
    )
)
registry.register(
    SimulatedDependencyCheck(
        "rabbitmq_orders",
        base_latency_ms=25,
        success_message="orders queue consumer connected",
        failure_message="AMQP channel closed",
    )
)
registry.register(health_check("worker_pool", worker_pool_check))
registry.register(
    SimulatedDependencyCheck(
        "elasticsearch_catalog",
        base_latency_ms=40,
        success_message="catalog index green",
        failure_message="cluster status red",
    )
)
registry.register(
    SimulatedDependencyCheck(
        "s3_media",
        base_latency_ms=60,
        success_message="media bucket writable",
        failure_message="bucket returned 403",
    )
)
registry.register(
    SimulatedDependencyCheck(
        "payments_api",
        base_latency_ms=120,
        success_message="payments provider responding",
        failure_message="payments provider timeout after 2000ms",
    )
)
registry.register(
    SimulatedDependencyCheck(
        "shipping_api",
        base_latency_ms=90,
        success_message="shipping quotes available",
        failure_message="shipping provider returned 502",
    )
)
registry.register(
    SimulatedDependencyCheck(
        "email_provider",
        base_latency_ms=70,
        success_message="transactional email accepted",
        failure_message="SMTP relay unavailable",
    )
)
registry.register(health_check("feature_flags", feature_flags_check))

DEPENDENCY_NAMES = [check.name for check in registry.checks]


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    async with engine.begin() as connection:
        await connection.execute(text("CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY)"))
        for version in ("0001_initial", "0002_orders", "0003_payments", "0004_catalog"):
            await connection.execute(
                text("INSERT OR IGNORE INTO schema_migrations (version) VALUES (:version)"),
                {"version": version},
            )
    yield
    await engine.dispose()


app = FastAPI(title="Enterprise Shop API", lifespan=lifespan)

install_health_check(app, registry, ui_title="Enterprise Shop — System Health")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def demo_console() -> str:
    rows = "".join(
        f"""
        <tr>
          <td><code>{name}</code></td>
          <td class="state state-{simulator.state(name)}">{simulator.state(name)}</td>
          <td>
            <a href="/demo/fail/{name}">fail</a>
            <a href="/demo/slow/{name}">slow</a>
            <a href="/demo/recover/{name}">recover</a>
          </td>
        </tr>
        """
        for name in DEPENDENCY_NAMES
    )

    return f"""
    <html>
      <head>
        <title>Enterprise Shop — health check demo</title>
        <style>
          body {{ font-family: ui-sans-serif, system-ui, sans-serif; margin: 2rem auto; max-width: 860px; color: #111; }}
          table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
          th, td {{ text-align: left; padding: .5rem .75rem; border-bottom: 1px solid #e5e5e5; }}
          a {{ margin-right: .5rem; }}
          .state-up {{ color: #15803d; }}
          .state-down {{ color: #b91c1c; }}
          .state-slow {{ color: #b45309; }}
          .links a {{ display: inline-block; margin: .25rem .75rem .25rem 0; }}
        </style>
      </head>
      <body>
        <h1>Enterprise Shop — health check demo</h1>
        <p class="links">
          <a href="/ht">/ht (HTML status page)</a>
          <a href="/health/live">/health/live</a>
          <a href="/health/ready">/health/ready</a>
          <a href="/docs">/docs</a>
          <a href="/demo/recover-all">recover everything</a>
        </p>
        <table>
          <tr><th>dependency</th><th>state</th><th>controls</th></tr>
          {rows}
        </table>
      </body>
    </html>
    """


def _assert_known(name: str) -> None:
    if name not in DEPENDENCY_NAMES:
        raise HTTPException(status_code=404, detail=f"unknown dependency '{name}'")


@app.get("/demo/fail/{name}", include_in_schema=False)
async def demo_fail(name: str) -> RedirectResponse:
    _assert_known(name)
    simulator.fail(name)
    return RedirectResponse("/", status_code=303)


@app.get("/demo/slow/{name}", include_in_schema=False)
async def demo_slow(name: str) -> RedirectResponse:
    _assert_known(name)
    simulator.slow(name)
    return RedirectResponse("/", status_code=303)


@app.get("/demo/recover/{name}", include_in_schema=False)
async def demo_recover(name: str) -> RedirectResponse:
    _assert_known(name)
    simulator.recover(name)
    return RedirectResponse("/", status_code=303)


@app.get("/demo/recover-all", include_in_schema=False)
async def demo_recover_all() -> RedirectResponse:
    simulator.recover_all()
    return RedirectResponse("/", status_code=303)

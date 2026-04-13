from __future__ import annotations

import asyncio

import pytest
from fastapi import FastAPI

from fastapi_health_check import HealthCheck, HealthRegistry, health_check, install_health_check


class PassingCheck(HealthCheck):
    async def check(self) -> str | None:
        return None


class MessageCheck(HealthCheck):
    async def check(self) -> str | None:
        return "dependency available"


class FailingCheck(HealthCheck):
    async def check(self) -> str | None:
        raise RuntimeError("dependency unavailable")


class SlowPassingCheck(HealthCheck):
    async def check(self) -> str | None:
        await asyncio.sleep(0.001)
        return None


@pytest.fixture
def registry_factory():
    def factory(*checks: HealthCheck) -> HealthRegistry:
        return HealthRegistry(checks)

    return factory


@pytest.fixture
def app_factory():
    def factory(
        registry: HealthRegistry,
        *,
        path: str = "/ht",
        ui_title: str = "System Health",
        include_in_schema: bool = False,
    ) -> FastAPI:
        app = FastAPI()
        install_health_check(
            app,
            registry,
            path=path,
            ui_title=ui_title,
            include_in_schema=include_in_schema,
        )
        return app

    return factory


@pytest.fixture
def passing_check() -> PassingCheck:
    return PassingCheck("passing")


@pytest.fixture
def message_check() -> MessageCheck:
    return MessageCheck("message")


@pytest.fixture
def failing_check() -> FailingCheck:
    return FailingCheck("failing")


@pytest.fixture
def slow_passing_check() -> SlowPassingCheck:
    return SlowPassingCheck("slow")


@pytest.fixture
def callable_check():
    return health_check("redis", lambda: "cache reachable")

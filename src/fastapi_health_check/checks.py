from __future__ import annotations

from collections.abc import Awaitable, Callable
from inspect import isawaitable
from abc import ABC, abstractmethod
from time import perf_counter

from fastapi_health_check.models import HealthCheckResult

CheckHandler = Callable[[], str | None | Awaitable[str | None]]


class HealthCheck(ABC):
    default_name = ""

    def __init__(self, name: str | None = None) -> None:
        resolved_name = name or self.default_name or self.__class__.__name__.removesuffix("Check").lower()
        if not resolved_name:
            msg = "health checks must define a name"
            raise ValueError(msg)

        self.name = resolved_name

    async def run(self) -> HealthCheckResult:
        started_at = perf_counter()

        try:
            message = await self.check()
        except Exception as exc:
            return HealthCheckResult(
                name=self.name,
                status="fail",
                message=str(exc),
                duration_ms=round((perf_counter() - started_at) * 1000, 3),
            )

        return HealthCheckResult(
            name=self.name,
            status="ok",
            message=message,
            duration_ms=round((perf_counter() - started_at) * 1000, 3),
        )

    @abstractmethod
    async def check(self) -> str | None:
        """Execute the health check and return an optional success message."""


class AppAliveCheck(HealthCheck):
    default_name = "app_alive"

    async def check(self) -> str | None:
        return None


class FunctionHealthCheck(HealthCheck):
    def __init__(self, name: str, handler: CheckHandler) -> None:
        super().__init__(name=name)
        self._handler = handler

    async def check(self) -> str | None:
        result = self._handler()
        if isawaitable(result):
            return await result

        return result


def health_check(name: str, handler: CheckHandler) -> FunctionHealthCheck:
    return FunctionHealthCheck(name=name, handler=handler)

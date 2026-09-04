from __future__ import annotations

import asyncio
from collections.abc import Iterable
from time import perf_counter

from fastapi_health_check.checks import HealthCheck
from fastapi_health_check.models import HealthReport


class HealthRegistry:
    def __init__(self, checks: Iterable[HealthCheck] | None = None) -> None:
        self._checks: list[HealthCheck] = []
        self._readiness_checks: list[HealthCheck] = []
        self._liveness_checks: list[HealthCheck] = []

        if checks is not None:
            for check in checks:
                self.register(check)

    @property
    def checks(self) -> tuple[HealthCheck, ...]:
        return tuple(self._checks)

    def register(
        self,
        check: HealthCheck,
        *,
        readiness: bool = True,
        liveness: bool = False,
    ) -> HealthCheck:
        if any(existing.name == check.name for existing in self._checks):
            msg = f"health check with name '{check.name}' is already registered"
            raise ValueError(msg)

        self._checks.append(check)
        if readiness:
            self._readiness_checks.append(check)
        if liveness:
            self._liveness_checks.append(check)
        return check

    async def run_checks(self) -> HealthReport:
        started_at = perf_counter()

        results = await asyncio.gather(*(check.run() for check in self._checks))

        report = HealthReport.from_checks(results)

        duration_ms = round((perf_counter() - started_at) * 1000, 3)

        return report.model_copy(update={"duration_ms": duration_ms})

    async def run_readiness_checks(self) -> HealthReport:
        results = [await check.run() for check in self._readiness_checks]
        return HealthReport.from_checks(results)

    async def run_liveness_checks(self) -> HealthReport:
        results = [await check.run() for check in self._liveness_checks]
        return HealthReport.from_checks(results)

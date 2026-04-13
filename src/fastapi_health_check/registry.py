from __future__ import annotations

from collections.abc import Iterable

from fastapi_health_check.checks import HealthCheck
from fastapi_health_check.models import HealthReport


class HealthRegistry:
    def __init__(self, checks: Iterable[HealthCheck] | None = None) -> None:
        self._checks: list[HealthCheck] = []

        if checks is not None:
            for check in checks:
                self.register(check)

    @property
    def checks(self) -> tuple[HealthCheck, ...]:
        return tuple(self._checks)

    def register(self, check: HealthCheck) -> HealthCheck:
        if any(existing.name == check.name for existing in self._checks):
            msg = f"health check with name '{check.name}' is already registered"
            raise ValueError(msg)

        self._checks.append(check)
        return check

    async def run_checks(self) -> HealthReport:
        results = [await check.run() for check in self._checks]
        return HealthReport.from_checks(results)

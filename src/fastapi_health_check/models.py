from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

HealthStatus = Literal["ok", "fail"]


class HealthCheckResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1)
    status: HealthStatus
    message: str | None = None
    duration_ms: float = Field(ge=0)


class HealthReport(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: HealthStatus
    checks: list[HealthCheckResult]

    @classmethod
    def from_checks(cls, checks: list[HealthCheckResult]) -> "HealthReport":
        status: HealthStatus = "fail" if any(check.status == "fail" for check in checks) else "ok"
        return cls(status=status, checks=checks)

    @property
    def is_healthy(self) -> bool:
        return self.status == "ok"

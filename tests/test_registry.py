from __future__ import annotations

import asyncio

import pytest

from fastapi_health_check import HealthCheck, HealthRegistry


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


def test_register_returns_registered_check() -> None:
    passing_check = PassingCheck("passing")
    registry = HealthRegistry()

    registered_check = registry.register(passing_check)

    assert registered_check is passing_check
    assert registry.checks == (passing_check,)


def test_register_rejects_duplicate_names() -> None:
    passing_check = PassingCheck("passing")
    registry = HealthRegistry([passing_check])

    with pytest.raises(ValueError, match="already registered"):
        registry.register(type(passing_check)("passing"))


def test_run_checks_preserves_registration_order() -> None:
    registry = HealthRegistry([PassingCheck("passing"), MessageCheck("message")])

    report = asyncio.run(registry.run_checks())

    assert report.status == "ok"
    assert [check.name for check in report.checks] == ["passing", "message"]


def test_run_checks_marks_report_as_failed_when_any_check_fails(
) -> None:
    registry = HealthRegistry([PassingCheck("passing"), FailingCheck("failing")])

    report = asyncio.run(registry.run_checks())

    assert report.status == "fail"
    assert [check.status for check in report.checks] == ["ok", "fail"]


def test_run_checks_with_empty_registry_returns_healthy_report() -> None:
    report = asyncio.run(HealthRegistry().run_checks())

    assert report.status == "ok"
    assert report.checks == []


def test_run_checks_tracks_execution_time() -> None:
    registry = HealthRegistry([SlowPassingCheck("slow")])

    report = asyncio.run(registry.run_checks())

    assert report.checks[0].duration_ms > 0

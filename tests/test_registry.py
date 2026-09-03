from __future__ import annotations

import asyncio
from functools import partial
from time import perf_counter

import pytest

from fastapi_health_check import HealthRegistry, health_check


def test_register_returns_registered_check(passing_check) -> None:
    registry = HealthRegistry()

    registered_check = registry.register(passing_check)

    assert registered_check is passing_check
    assert registry.checks == (passing_check,)


def test_register_rejects_duplicate_names(passing_check) -> None:
    registry = HealthRegistry([passing_check])

    with pytest.raises(ValueError, match="already registered"):
        registry.register(type(passing_check)("passing"))


def test_run_checks_preserves_registration_order(registry_factory, passing_check, message_check) -> None:
    registry = registry_factory(passing_check, message_check)

    report = asyncio.run(registry.run_checks())

    assert report.status == "ok"
    assert [check.name for check in report.checks] == ["passing", "message"]


def test_run_checks_marks_report_as_failed_when_any_check_fails(
    registry_factory,
    passing_check,
    failing_check,
) -> None:
    registry = registry_factory(passing_check, failing_check)

    report = asyncio.run(registry.run_checks())

    assert report.status == "fail"
    assert [check.status for check in report.checks] == ["ok", "fail"]


def test_run_checks_with_empty_registry_returns_healthy_report() -> None:
    report = asyncio.run(HealthRegistry().run_checks())

    assert report.status == "ok"
    assert report.checks == []


def test_run_checks_tracks_execution_time(registry_factory, slow_passing_check) -> None:
    registry = registry_factory(slow_passing_check)

    report = asyncio.run(registry.run_checks())

    assert report.checks[0].duration_ms > 0


def test_registry_accepts_function_based_checks(registry_factory, callable_check) -> None:
    report = asyncio.run(registry_factory(callable_check).run_checks())

    assert report.status == "ok"
    assert report.checks[0].name == "redis"
    assert report.checks[0].message == "cache reachable"


def test_run_checks_executes_async_checks_concurrently_in_registration_order() -> None:
    async def delayed_result(message: str, delay: float) -> str:
        await asyncio.sleep(delay)
        return message

    registry = HealthRegistry(
        [
            health_check("slow", partial(delayed_result, "slow result", 0.3)),
            health_check("fast", partial(delayed_result, "fast result", 0.05)),
            health_check("medium", partial(delayed_result, "medium result", 0.15)),
        ]
    )

    started_at = perf_counter()
    report = asyncio.run(registry.run_checks())
    elapsed = perf_counter() - started_at

    assert elapsed < 0.4
    assert [check.name for check in report.checks] == ["slow", "fast", "medium"]
    assert [check.message for check in report.checks] == [
        "slow result",
        "fast result",
        "medium result",
    ]

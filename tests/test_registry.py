from __future__ import annotations

import asyncio
from functools import partial
from threading import Event
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


def test_run_checks_does_not_block_the_event_loop_for_sync_handlers() -> None:
    release_handler = Event()

    def blocking_handler() -> str:
        release_handler.wait(timeout=1)
        return "sync result"

    async def release_from_event_loop() -> None:
        await asyncio.sleep(0.05)
        release_handler.set()

    async def run_scenario():
        return await asyncio.gather(
            HealthRegistry([health_check("sync", blocking_handler)]).run_checks(),
            release_from_event_loop(),
        )

    started_at = perf_counter()
    report, _ = asyncio.run(run_scenario())
    elapsed = perf_counter() - started_at

    assert elapsed < 0.5
    assert report.checks[0].message == "sync result"
def test_registered_checks_belong_to_readiness_by_default(passing_check) -> None:
    registry = HealthRegistry([passing_check])

    readiness_report = asyncio.run(registry.run_readiness_checks())
    liveness_report = asyncio.run(registry.run_liveness_checks())

    assert [check.name for check in readiness_report.checks] == ["passing"]
    assert liveness_report.checks == []


def test_register_can_assign_a_check_to_liveness_only(failing_check) -> None:
    registry = HealthRegistry()
    registry.register(failing_check, readiness=False, liveness=True)

    readiness_report = asyncio.run(registry.run_readiness_checks())
    liveness_report = asyncio.run(registry.run_liveness_checks())

    assert readiness_report.status == "ok"
    assert readiness_report.checks == []
    assert liveness_report.status == "fail"
    assert [check.name for check in liveness_report.checks] == ["failing"]


def test_register_can_assign_a_check_to_both_probes(passing_check) -> None:
    registry = HealthRegistry()
    registry.register(passing_check, readiness=True, liveness=True)

    readiness_report = asyncio.run(registry.run_readiness_checks())
    liveness_report = asyncio.run(registry.run_liveness_checks())

    assert [check.name for check in readiness_report.checks] == ["passing"]
    assert [check.name for check in liveness_report.checks] == ["passing"]

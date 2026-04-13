from __future__ import annotations

import asyncio

from fastapi_health_check import AppAliveCheck


def test_health_check_run_returns_success_result(message_check) -> None:
    result = asyncio.run(message_check.run())

    assert result.name == "message"
    assert result.status == "ok"
    assert result.message == "dependency available"
    assert result.duration_ms >= 0


def test_health_check_run_returns_failure_result_on_exception(failing_check) -> None:
    result = asyncio.run(failing_check.run())

    assert result.name == "failing"
    assert result.status == "fail"
    assert result.message == "dependency unavailable"
    assert result.duration_ms >= 0


def test_app_alive_check_has_default_name_and_succeeds() -> None:
    result = asyncio.run(AppAliveCheck().run())

    assert result.name == "app_alive"
    assert result.status == "ok"
    assert result.message is None

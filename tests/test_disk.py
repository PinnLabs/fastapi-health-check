from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi_health_check import DiskSpaceCheck


def test_disk_space_check_succeeds_when_threshold_is_met(tmp_path: Path) -> None:
    result = asyncio.run(
        DiskSpaceCheck(
            path=tmp_path,
            min_free_bytes=1,
        ).run()
    )

    assert result.name == "disk_space"
    assert result.status == "ok"
    assert result.message is not None
    assert "bytes free" in result.message


def test_disk_space_check_fails_when_byte_threshold_is_not_met(tmp_path: Path) -> None:
    result = asyncio.run(
        DiskSpaceCheck(
            path=tmp_path,
            min_free_bytes=10**18,
        ).run()
    )

    assert result.name == "disk_space"
    assert result.status == "fail"
    assert result.message is not None
    assert "below required threshold" in result.message


def test_disk_space_check_fails_when_percent_threshold_is_not_met(
    tmp_path: Path,
) -> None:
    result = asyncio.run(
        DiskSpaceCheck(
            path=tmp_path,
            min_free_percent=100.0,
        ).run()
    )

    assert result.name == "disk_space"
    assert result.status == "fail"
    assert result.message is not None
    assert "below required threshold" in result.message


def test_disk_space_check_handles_invalid_path(tmp_path: Path) -> None:
    missing_path = tmp_path / "does-not-exist"

    result = asyncio.run(
        DiskSpaceCheck(
            path=missing_path,
            min_free_bytes=1,
        ).run()
    )

    assert result.name == "disk_space"
    assert result.status == "fail"
    assert result.message is not None
    assert "unable to check disk space" in result.message


def test_disk_space_check_requires_a_threshold() -> None:
    try:
        DiskSpaceCheck()
    except ValueError as exc:
        assert str(exc) == "at least one disk space threshold must be provided"
    else:
        raise AssertionError("DiskSpaceCheck should require a threshold")

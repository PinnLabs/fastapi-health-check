from __future__ import annotations

import shutil
from pathlib import Path

from fastapi_health_check.checks import HealthCheck


class DiskSpaceCheck(HealthCheck):
    default_name = "disk_space"

    def __init__(
        self,
        path: str | Path = ".",
        *,
        min_free_bytes: int | None = None,
        min_free_percent: float | None = None,
        name: str | None = None,
    ) -> None:
        super().__init__(name=name)

        if min_free_bytes is None and min_free_percent is None:
            raise ValueError("at least one disk space threshold must be provided")

        if min_free_bytes is not None and min_free_bytes < 0:
            raise ValueError("min_free_bytes must be non-negative")

        if min_free_percent is not None and not 0 <= min_free_percent <= 100:
            raise ValueError("min_free_percent must be between 0 and 100")

        self.path = Path(path)
        self.min_free_bytes = min_free_bytes
        self.min_free_percent = min_free_percent

    async def check(self) -> str:
        try:
            usage = shutil.disk_usage(self.path)
        except OSError as exc:
            raise RuntimeError(f"unable to check disk space for {self.path}") from exc

        free_percent = (usage.free / usage.total) * 100 if usage.total else 0.0

        if self.min_free_bytes is not None and usage.free < self.min_free_bytes:
            raise RuntimeError(
                f"disk free space below required threshold: "
                f"{usage.free} bytes available"
            )

        if self.min_free_percent is not None and free_percent < self.min_free_percent:
            raise RuntimeError(
                f"disk free space below required threshold: "
                f"{free_percent:.2f}% available"
            )

        return f"{usage.free} bytes free ({free_percent:.2f}% available) on {self.path}"

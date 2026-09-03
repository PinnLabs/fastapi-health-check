from __future__ import annotations

from typing import Any

from fastapi_health_check.checks import HealthCheck


class SQLAlchemyCheck(HealthCheck):
    default_name = "sqlalchemy"

    def __init__(self, bind: Any, name: str | None = None) -> None:
        super().__init__(name=name)
        self._bind = bind

    async def check(self) -> str:
        from sqlalchemy import text

        async with self._bind.connect() as connection:
            await connection.execute(text("SELECT 1"))

        return "SQLAlchemy available"

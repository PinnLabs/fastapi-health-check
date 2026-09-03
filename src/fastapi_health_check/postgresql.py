from __future__ import annotations

from contextlib import AbstractAsyncContextManager
from typing import Protocol

from fastapi_health_check.checks import HealthCheck


class PostgreSQLConnection(Protocol):
    async def execute(self, query: str) -> object: ...


class PostgreSQLPool(Protocol):
    def acquire(self) -> AbstractAsyncContextManager[PostgreSQLConnection]: ...


class PostgreSQLCheck(HealthCheck):
    default_name = "postgresql"

    def __init__(self, pool: PostgreSQLPool, name: str | None = None) -> None:
        super().__init__(name=name)
        self._pool = pool

    async def check(self) -> str:
        async with self._pool.acquire() as connection:
            await connection.execute("SELECT 1")

        return "PostgreSQL available"

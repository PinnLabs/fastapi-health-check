from __future__ import annotations

import asyncio

from fastapi_health_check import PostgreSQLCheck


class AvailableConnection:
    def __init__(self) -> None:
        self.executed_query: str | None = None

    async def execute(self, query: str) -> None:
        self.executed_query = query


class ConnectionLease:
    def __init__(self, connection: AvailableConnection) -> None:
        self.connection = connection
        self.released = False

    async def __aenter__(self) -> AvailableConnection:
        return self.connection

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        self.released = True


class ExistingPool:
    def __init__(self, lease: ConnectionLease) -> None:
        self.lease = lease

    def acquire(self) -> ConnectionLease:
        return self.lease


def test_postgresql_check_reuses_pool_and_executes_lightweight_query() -> None:
    connection = AvailableConnection()
    lease = ConnectionLease(connection)
    pool = ExistingPool(lease)

    result = asyncio.run(PostgreSQLCheck(pool, name="primary_database").run())

    assert result.name == "primary_database"
    assert result.status == "ok"
    assert result.message == "PostgreSQL available"
    assert connection.executed_query == "SELECT 1"
    assert lease.released is True

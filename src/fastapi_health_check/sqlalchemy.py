from __future__ import annotations

import asyncio
from typing import Any

from fastapi_health_check.checks import HealthCheck


class SQLAlchemyCheck(HealthCheck):
    default_name = "sqlalchemy"

    def __init__(self, bind: Any, name: str | None = None) -> None:
        super().__init__(name=name)
        self._bind = bind

    async def check(self) -> str:
        from sqlalchemy import text
        from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker
        from sqlalchemy.orm import sessionmaker

        statement = text("SELECT 1")
        if isinstance(self._bind, AsyncEngine):
            async with self._bind.connect() as connection:
                await connection.execute(statement)
        elif isinstance(self._bind, async_sessionmaker):
            async with self._bind() as session:
                await session.execute(statement)
        elif isinstance(self._bind, sessionmaker):
            await asyncio.to_thread(self._check_sync_session_factory, statement)
        else:
            await asyncio.to_thread(self._check_sync_engine, statement)

        return "SQLAlchemy available"

    def _check_sync_engine(self, statement: Any) -> None:
        with self._bind.connect() as connection:
            connection.execute(statement)

    def _check_sync_session_factory(self, statement: Any) -> None:
        with self._bind() as session:
            session.execute(statement)

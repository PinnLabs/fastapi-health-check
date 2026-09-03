from __future__ import annotations

import asyncio

from sqlalchemy.ext.asyncio import create_async_engine

from fastapi_health_check import SQLAlchemyCheck


def test_sqlalchemy_check_supports_async_engine() -> None:
    async def run_check():
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        try:
            return await SQLAlchemyCheck(engine, name="primary_database").run()
        finally:
            await engine.dispose()

    result = asyncio.run(run_check())

    assert result.name == "primary_database"
    assert result.status == "ok"
    assert result.message == "SQLAlchemy available"

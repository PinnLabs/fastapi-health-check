from __future__ import annotations

import asyncio
import sqlite3
from threading import Event
from time import perf_counter

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

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


def test_sqlalchemy_check_runs_sync_engine_without_blocking_event_loop() -> None:
    release_connection = Event()

    def connect() -> sqlite3.Connection:
        release_connection.wait(timeout=1)
        return sqlite3.connect(":memory:", check_same_thread=False)

    engine = create_engine("sqlite://", creator=connect)

    async def release_from_event_loop() -> None:
        await asyncio.sleep(0.05)
        release_connection.set()

    async def run_scenario():
        return await asyncio.gather(
            SQLAlchemyCheck(engine).run(),
            release_from_event_loop(),
        )

    started_at = perf_counter()
    result, _ = asyncio.run(run_scenario())
    elapsed = perf_counter() - started_at
    engine.dispose()

    assert elapsed < 0.5
    assert result.status == "ok"
    assert result.message == "SQLAlchemy available"


def test_sqlalchemy_check_supports_async_session_factory() -> None:
    async def run_check():
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        try:
            sessions = async_sessionmaker(engine)
            return await SQLAlchemyCheck(sessions).run()
        finally:
            await engine.dispose()

    result = asyncio.run(run_check())

    assert result.status == "ok"
    assert result.message == "SQLAlchemy available"

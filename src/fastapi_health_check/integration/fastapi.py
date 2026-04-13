from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from fastapi_health_check.registry import HealthRegistry


def install_health_check(
    app: FastAPI,
    registry: HealthRegistry,
    *,
    path: str = "/health",
    include_in_schema: bool = False,
) -> None:
    async def health_endpoint() -> JSONResponse:
        report = await registry.run_checks()
        status_code = 200 if report.is_healthy else 503
        return JSONResponse(status_code=status_code, content=report.model_dump(mode="json"))

    app.add_api_route(
        path,
        health_endpoint,
        methods=["GET"],
        include_in_schema=include_in_schema,
        name="health_check",
    )

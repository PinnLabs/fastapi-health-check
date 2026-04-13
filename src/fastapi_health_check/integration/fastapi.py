from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response

from fastapi_health_check.registry import HealthRegistry
from fastapi_health_check.ui import render_health_report_page


def install_health_check(
    app: FastAPI,
    registry: HealthRegistry,
    *,
    path: str = "/ht",
    ui_title: str = "System Health",
    include_in_schema: bool = False,
) -> None:
    async def health_endpoint(request: Request) -> Response:
        report = await registry.run_checks()
        status_code = 200 if report.is_healthy else 503
        accept = request.headers.get("accept", "")
        prefers_json = "application/json" in accept and "text/html" not in accept

        if prefers_json:
            return JSONResponse(status_code=status_code, content=report.model_dump(mode="json"))

        content = render_health_report_page(report, title=ui_title)
        return HTMLResponse(status_code=status_code, content=content)

    app.add_api_route(
        path,
        health_endpoint,
        methods=["GET"],
        include_in_schema=include_in_schema,
        name="health_check",
    )

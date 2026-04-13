from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_health_check import HealthCheck, HealthRegistry, install_health_check


class PassingCheck(HealthCheck):
    async def check(self) -> str | None:
        return None


class FailingCheck(HealthCheck):
    async def check(self) -> str | None:
        raise RuntimeError("dependency unavailable")


def build_app(
    registry: HealthRegistry,
    *,
    path: str = "/health",
    include_in_schema: bool = False,
) -> FastAPI:
    app = FastAPI()
    install_health_check(app, registry, path=path, include_in_schema=include_in_schema)
    return app


def test_health_endpoint_returns_200_for_healthy_registry() -> None:
    app = build_app(HealthRegistry([PassingCheck("passing")]))
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "checks": [
            {
                "name": "passing",
                "status": "ok",
                "message": None,
                "duration_ms": response.json()["checks"][0]["duration_ms"],
            }
        ],
    }
    assert response.json()["checks"][0]["duration_ms"] >= 0


def test_health_endpoint_returns_503_for_unhealthy_registry(
) -> None:
    app = build_app(HealthRegistry([PassingCheck("passing"), FailingCheck("failing")]))
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 503
    assert response.json()["status"] == "fail"
    assert response.json()["checks"][1]["message"] == "dependency unavailable"


def test_health_endpoint_accepts_custom_path() -> None:
    app = build_app(HealthRegistry([PassingCheck("passing")]), path="/status")
    client = TestClient(app)

    response = client.get("/status")

    assert response.status_code == 200
    assert client.get("/health").status_code == 404


def test_health_endpoint_is_hidden_from_openapi_by_default() -> None:
    app = build_app(HealthRegistry([PassingCheck("passing")]))
    client = TestClient(app)

    response = client.get("/openapi.json")

    assert "/health" not in response.json()["paths"]


def test_health_endpoint_can_be_included_in_openapi() -> None:
    app = build_app(HealthRegistry([PassingCheck("passing")]), include_in_schema=True)
    client = TestClient(app)

    response = client.get("/openapi.json")

    assert "/health" in response.json()["paths"]

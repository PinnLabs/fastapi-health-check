from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

from fastapi_health_check import HealthRegistry, health_check


def test_health_endpoint_returns_html_by_default(app_factory, registry_factory, passing_check) -> None:
    app = app_factory(registry_factory(passing_check))
    client = TestClient(app)

    response = client.get("/ht")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "FastAPI Health Check" in response.text
    assert "Healthy" in response.text


def test_health_endpoint_returns_json_when_requested(app_factory, registry_factory, passing_check) -> None:
    app = app_factory(registry_factory(passing_check))
    client = TestClient(app)

    response = client.get("/ht", headers={"accept": "application/json"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
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
        "duration_ms": response.json()["duration_ms"],
    }
    assert response.json()["checks"][0]["duration_ms"] >= 0


def test_health_endpoint_returns_503_for_unhealthy_registry(
    app_factory,
    registry_factory,
    passing_check,
    failing_check,
) -> None:
    app = app_factory(registry_factory(passing_check, failing_check))
    client = TestClient(app)

    response = client.get("/ht", headers={"accept": "application/json"})

    assert response.status_code == 503
    assert response.json()["status"] == "fail"
    assert response.json()["checks"][1]["message"] == "dependency unavailable"


def test_health_endpoint_accepts_custom_path(app_factory, registry_factory, passing_check) -> None:
    app = app_factory(registry_factory(passing_check), path="/status")
    client = TestClient(app)

    response = client.get("/status")

    assert response.status_code == 200
    assert client.get("/ht").status_code == 404


def test_health_endpoint_is_hidden_from_openapi_by_default(
    app_factory,
    registry_factory,
    passing_check,
) -> None:
    app = app_factory(registry_factory(passing_check))
    client = TestClient(app)

    response = client.get("/openapi.json")

    assert "/ht" not in response.json()["paths"]


def test_health_endpoint_can_be_included_in_openapi(app_factory, registry_factory, passing_check) -> None:
    app = app_factory(registry_factory(passing_check), include_in_schema=True)
    client = TestClient(app)

    response = client.get("/openapi.json")

    assert "/ht" in response.json()["paths"]


def test_health_endpoint_renders_html_for_healthy_registry(app_factory, registry_factory, message_check) -> None:
    app = app_factory(registry_factory(message_check))
    client = TestClient(app)

    response = client.get("/ht")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "FastAPI Health Check" in response.text
    assert "Healthy" in response.text
    assert "dependency available" in response.text


def test_health_endpoint_renders_html_for_unhealthy_registry(
    app_factory,
    registry_factory,
    passing_check,
    failing_check,
) -> None:
    app = app_factory(registry_factory(passing_check, failing_check))
    client = TestClient(app)

    response = client.get("/ht")

    assert response.status_code == 503
    assert "Issues detected" in response.text
    assert "dependency unavailable" in response.text


def test_health_endpoint_accepts_custom_title(app_factory, registry_factory, passing_check) -> None:
    app = app_factory(registry_factory(passing_check), ui_title="API Operations")
    client = TestClient(app)

    response = client.get("/ht")

    assert "API Operations" in response.text


def test_health_endpoint_returns_503_instead_of_500_for_invalid_check_result(
    app_factory,
    registry_factory,
) -> None:
    bad_handler: Any = lambda: {"ok": True}
    app = app_factory(registry_factory(health_check("invalid", bad_handler)))
    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/ht", headers={"accept": "application/json"})

    assert response.status_code == 503
    assert response.json() == {
        "status": "fail",
        "checks": [
            {
                "name": "invalid",
                "status": "fail",
                "message": "health checks must return a string or None",
                "duration_ms": response.json()["checks"][0]["duration_ms"],
            }
        ],
        "duration_ms": response.json()["duration_ms"],

    }
    assert response.json()["checks"][0]["duration_ms"] >= 0


def test_health_endpoint_renders_html_for_invalid_check_result(
    app_factory,
    registry_factory,
) -> None:
    bad_handler: Any = lambda: {"ok": True}
    app = app_factory(registry_factory(health_check("invalid", bad_handler)))
    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/ht")

    assert response.status_code == 503
    assert "Issues detected" in response.text
    assert "health checks must return a string or None" in response.text


def test_readiness_endpoint_returns_a_healthy_json_report(app_factory, registry_factory, passing_check) -> None:
    app = app_factory(registry_factory(passing_check))
    client = TestClient(app)

    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
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
        "duration_ms": response.json()["duration_ms"],
    }


def test_readiness_failure_does_not_fail_liveness_by_default(
    app_factory,
    registry_factory,
    failing_check,
) -> None:
    app = app_factory(registry_factory(failing_check))
    client = TestClient(app)

    readiness_response = client.get("/health/ready")
    liveness_response = client.get("/health/live")

    assert readiness_response.status_code == 503
    assert readiness_response.json()["status"] == "fail"
    assert readiness_response.json()["checks"][0]["name"] == "failing"
    assert liveness_response.status_code == 200
    assert liveness_response.json() == {"status": "ok", "checks": [],"duration_ms": None,}


def test_liveness_endpoint_returns_an_unhealthy_json_report(app_factory, failing_check) -> None:
    registry = HealthRegistry()
    registry.register(failing_check, readiness=False, liveness=True)
    app = app_factory(registry)
    client = TestClient(app)

    response = client.get("/health/live")

    assert response.status_code == 503
    assert response.json()["status"] == "fail"
    assert response.json()["checks"][0]["name"] == "failing"


def test_probe_endpoints_accept_independent_custom_paths(app_factory, registry_factory, passing_check) -> None:
    app = app_factory(
        registry_factory(passing_check),
        liveness_path="/livez",
        readiness_path="/readyz",
    )
    client = TestClient(app)

    assert client.get("/livez").status_code == 200
    assert client.get("/readyz").status_code == 200
    assert client.get("/health/live").status_code == 404
    assert client.get("/health/ready").status_code == 404

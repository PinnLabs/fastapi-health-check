from __future__ import annotations

from fastapi.testclient import TestClient


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

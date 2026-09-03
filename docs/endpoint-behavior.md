# Endpoint Behavior

## Default routes

By default, `install_health_check()` exposes:

```text
GET /ht
GET /health/live
GET /health/ready
```

## Response mode

The combined endpoint serves different representations depending on the request. Both probe endpoints always return JSON using the `HealthReport` and `HealthCheckResult` schema.

### Browser access

When opened in a browser, `/ht` returns an HTML page designed for quick visual inspection.

### JSON clients

When the client sends:

```text
Accept: application/json
```

the route returns JSON.

## Status codes

- `200` when all checks are healthy
- `503` when at least one check fails

## Probe behavior

Checks registered without probe options belong to readiness. This keeps external dependencies out of liveness by default.

```python
registry.register(database_check)
registry.register(process_check, readiness=False, liveness=True)
registry.register(app_alive_check, readiness=True, liveness=True)
```

The combined `/ht` endpoint continues to run every registered check regardless of probe membership.

## Custom paths

You can configure all paths independently.

```python
install_health_check(
    app,
    registry,
    path="/status",
    liveness_path="/livez",
    readiness_path="/readyz",
)
```

## Kubernetes usage

Point the Kubernetes liveness probe at `/health/live`. Liveness should contain only inexpensive checks that determine whether the application process needs to be restarted.

Point the Kubernetes readiness probe at `/health/ready`. Readiness can contain databases, caches, queues, and external services that must be available before the application receives traffic.

Keeping dependency checks out of liveness prevents a temporary dependency outage from restarting a healthy process. A readiness failure instead allows Kubernetes to remove the pod from service until it recovers.

## OpenAPI inclusion

The routes are hidden from the schema by default.

You can include them with:

```python
install_health_check(app, registry, include_in_schema=True)
```

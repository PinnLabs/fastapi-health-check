# Endpoint Behavior

## Default route

By default, `install_health_check()` exposes:

```text
GET /ht
```

## Response mode

The endpoint serves different representations depending on the request.

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

## Custom path

You can override the default path.

```python
install_health_check(app, registry, path="/status")
```

## OpenAPI inclusion

The route is hidden from the schema by default.

You can include it with:

```python
install_health_check(app, registry, include_in_schema=True)
```

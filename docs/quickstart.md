# Quickstart

This is the smallest useful setup for a FastAPI application.

```python
from fastapi import FastAPI

from fastapi_health_check import AppAliveCheck, HealthRegistry, health_check, install_health_check


app = FastAPI()
registry = HealthRegistry(
    [
        AppAliveCheck(),
        health_check("database", lambda: "connection ok"),
        health_check("redis", lambda: "cache reachable"),
    ]
)

install_health_check(app, registry)
```

## Result

This exposes `GET /ht`.

- In the browser, the route renders the health page
- For programmatic clients, the same route returns JSON when `Accept: application/json` is sent

## Example JSON request

```bash
curl -H "Accept: application/json" http://127.0.0.1:8000/ht
```

## Example browser URL

```text
http://127.0.0.1:8000/ht
```

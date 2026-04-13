from fastapi import FastAPI
from fastapi_health_check import (
    AppAliveCheck,
    HealthRegistry,
    health_check,
    install_health_check,
)


app = FastAPI()
registry = HealthRegistry(
    [
        AppAliveCheck(),
        health_check("database", lambda: "connection ok"),
        health_check("redis", lambda: "cache reachable"),
    ]
)

install_health_check(app, registry)

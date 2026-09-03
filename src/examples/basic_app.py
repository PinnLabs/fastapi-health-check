from fastapi import FastAPI
from fastapi_health_check import (
    AppAliveCheck,
    HealthRegistry,
    health_check,
    install_health_check,
)


app = FastAPI()
registry = HealthRegistry()
registry.register(AppAliveCheck(), readiness=True, liveness=True)
registry.register(health_check("database", lambda: "connection ok"))
registry.register(health_check("redis", lambda: "cache reachable"))

install_health_check(app, registry)

from fastapi import FastAPI
from fastapi_health_check import (
    AppAliveCheck,
    HealthCheck,
    HealthRegistry,
    install_health_check,
)


class DatabaseCheck(HealthCheck):
    default_name = "database"

    async def check(self) -> str | None:
        return "connection ok"


app = FastAPI()
registry = HealthRegistry([AppAliveCheck(), DatabaseCheck()])

install_health_check(app, registry)

# fastapi-health-check

Biblioteca para expor health checks em aplicações FastAPI com uma API mínima:

- contrato base para checks
- registro e execução agregada
- instalação rápida de endpoint `/health`

## Exemplo

```python
from fastapi import FastAPI

from fastapi_health_check import AppAliveCheck, HealthCheck, HealthRegistry, install_health_check


class DatabaseCheck(HealthCheck):
    default_name = "database"

    async def check(self) -> str | None:
        # execute um SELECT 1 aqui
        return None


app = FastAPI()
registry = HealthRegistry([AppAliveCheck(), DatabaseCheck()])

install_health_check(app, registry)
```

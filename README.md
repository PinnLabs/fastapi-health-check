# fastapi-health-check

Biblioteca para expor health checks em aplicações FastAPI com uma API mínima:

- contrato base para checks
- registro e execução agregada
- instalação rápida de endpoint único em `/ht`
- resposta HTML para navegação no browser e JSON para clientes que pedirem `application/json`

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

Isso expõe `GET /ht`.
No navegador, a rota renderiza uma tela HTML.
Para integrações automatizadas, a mesma rota responde JSON quando o cliente envia `Accept: application/json`.

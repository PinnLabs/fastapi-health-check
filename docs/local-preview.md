# Local Preview

The repository includes a runnable example application:

```text
src/examples/basic_app.py
```

## Run the example app

```bash
uv run uvicorn src.examples.basic_app:app --reload
```

## Open the endpoint

- HTML: `http://127.0.0.1:8000/ht`
- JSON:

```bash
curl -H "Accept: application/json" http://127.0.0.1:8000/ht
```

## Run the documentation locally

```bash
uv run mkdocs serve
```

This starts the documentation site with live reload, usually at:

```text
http://127.0.0.1:8000
```

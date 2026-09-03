# Installation

## Install with uv

```bash
uv add fastapi-ht
```

## Install with pip

```bash
pip install fastapi-ht
```

## Requirements

- Python 3.12+
- FastAPI application

## Optional SQLAlchemy support

Install the SQLAlchemy integration only when the application needs it:

```bash
uv add "fastapi-ht[sqlalchemy]"
```

```bash
pip install "fastapi-ht[sqlalchemy]"
```

The extra installs SQLAlchemy `>=2.0,<3.0` with async support. The core `fastapi-ht` installation does not depend on SQLAlchemy.

## What gets installed

The package includes:

- the health check registry
- the check base classes
- the function-based `health_check()` helper
- the built-in HTML UI renderer
- the FastAPI integration layer

# fastapi-ht

FastAPI health checks with a visual status page, a JSON response mode, and a small API for custom monitoring.

<p align="center">
  <img src="https://raw.githubusercontent.com/PinnLabs/fastapi-health-check/main/public/logo.png" alt="fastapi-ht logo" width="220" />
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/PinnLabs/fastapi-health-check/main/public/example_use.png" alt="fastapi-ht example interface" width="100%" />
</p>

## Why fastapi-ht

- One endpoint, `/ht`, for both browser-friendly HTML and JSON clients
- A lightweight registry for grouping health checks
- A simple `health_check()` API for custom checks
- Class-based checks for advanced use cases
- A built-in visual page for operational inspection

## Built for practical monitoring

The library does not ship with a database integration by default.

Instead, it gives you the primitives to monitor what matters in your own backend:

- databases
- Redis or cache layers
- queues
- external APIs
- storage backends
- internal services and domain-specific dependencies

## Start here

- [Installation](installation.md)
- [Quickstart](quickstart.md)
- [Custom Checks](custom-checks.md)
- [Endpoint Behavior](endpoint-behavior.md)

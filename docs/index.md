# fastapi-ht

FastAPI health checks with separate liveness and readiness probes, a visual status page, and a small API for custom monitoring.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/PinnLabs/fastapi-health-check/main/public/logo-dark.png">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/PinnLabs/fastapi-health-check/main/public/logo-light.png">
    <img src="https://raw.githubusercontent.com/PinnLabs/fastapi-health-check/main/public/logo-light.png" alt="fastapi-ht logo" width="220" />
  </picture>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/PinnLabs/fastapi-health-check/main/public/example_use.png" alt="fastapi-ht example interface" width="100%" />
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/PinnLabs/fastapi-health-check/main/public/example_failure.png" alt="fastapi-ht example interface with a failing dependency" width="100%" />
</p>

## Why fastapi-ht

- Separate `/health/live` and `/health/ready` JSON probes
- A combined `/ht` endpoint for browser-friendly HTML and JSON clients
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

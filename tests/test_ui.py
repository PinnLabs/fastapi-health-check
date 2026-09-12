from datetime import UTC, datetime

from fastapi_health_check.models import HealthCheckResult, HealthReport
from fastapi_health_check.ui import render_health_report_page


def test_render_health_report_shows_check_duration() -> None:
    report = HealthReport(
        status="ok",
        checks=[
            HealthCheckResult(
                name="redis",
                status="ok",
                message="cache reachable",
                duration_ms=12.345,
            )
        ],
        duration_ms=15.678,
    )

    html = render_health_report_page(report)

    assert "12.35 ms" in html


def test_render_health_report_formats_sub_millisecond_duration() -> None:
    report = HealthReport(
        status="ok",
        checks=[
            HealthCheckResult(
                name="fast_check",
                status="ok",
                duration_ms=0.5,
            )
        ],
        duration_ms=0.8,
    )

    html = render_health_report_page(report)

    assert "500 µs" in html


def test_render_health_report_formats_multi_second_duration() -> None:
    report = HealthReport(
        status="ok",
        checks=[
            HealthCheckResult(
                name="slow_check",
                status="ok",
                duration_ms=1234.56,
            )
        ],
        duration_ms=2345.67,
    )

    html = render_health_report_page(report)

    assert "1.23 s" in html


def test_render_health_report_builds_minimal_diagnostic_header() -> None:
    report = HealthReport(status="ok", checks=[], duration_ms=8.7)

    html = render_health_report_page(
        report,
        title="Payments API",
        endpoint="/status",
        liveness_endpoint="/livez",
        readiness_endpoint="/readyz",
        generated_at=datetime(2026, 9, 12, 14, 24, 36, 492000, tzinfo=UTC),
    )

    assert "System Diagnostic" not in html
    assert "Diagnostic Checks" in html
    assert 'href="/status"' in html
    assert 'href="/livez"' in html
    assert 'href="/readyz"' in html
    assert "2026-09-12 / 14:24:36.492 UTC" in html
    assert "No health checks are currently registered" in html
    assert "Built by PinnLabs" in html
    assert 'href="https://www.pinnlabs.tech"' in html


def test_render_health_report_uses_expandable_rows_and_escapes_values() -> None:
    report = HealthReport(
        status="fail",
        checks=[
            HealthCheckResult(
                name='<script id="name">',
                status="fail",
                message='<img src=x onerror="alert(1)">',
                duration_ms=1000,
            )
        ],
        duration_ms=1000,
    )

    html = render_health_report_page(report, title="API <unsafe>")

    assert '<details class="check-record"' in html
    assert "trace__line" in html
    assert "unhealthy" in html
    assert "&lt;script id=&quot;name&quot;&gt;" in html
    assert "&lt;img src=x onerror=&quot;alert(1)&quot;&gt;" in html
    assert '<script id="name">' not in html
    assert "◌" in html

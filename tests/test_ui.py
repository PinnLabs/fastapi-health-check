from datetime import UTC, datetime

import pytest

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


@pytest.mark.parametrize(
    ("time_zone", "expected"),
    [
        ("UTC-03:00", "2026-09-18 / 19:52:52.466 UTC-03:00"),
        ("America/Fortaleza", "2026-09-18 / 19:52:52.466 UTC-03:00"),
        ("America/New_York", "2026-09-18 / 18:52:52.466 UTC-04:00"),
        ("UTC+05:30", "2026-09-19 / 04:22:52.466 UTC+05:30"),
    ],
)
def test_render_health_report_uses_configured_time_zone(
    time_zone: str, expected: str
) -> None:
    report = HealthReport(
        status="ok",
        checks=[HealthCheckResult(name="redis", status="ok", duration_ms=1)],
        duration_ms=1,
    )

    html = render_health_report_page(
        report,
        generated_at=datetime(2026, 9, 18, 22, 52, 52, 466000, tzinfo=UTC),
        time_zone=time_zone,
    )

    assert expected in html
    assert 'data-time-zone="' + time_zone + '"' in html
    assert f"data-detail-checked-at>{expected.split(' / ')[1]}</span>" in html


def test_render_health_report_uses_winter_offset_for_iana_zone() -> None:
    report = HealthReport(status="ok", checks=[], duration_ms=0)

    html = render_health_report_page(
        report,
        generated_at=datetime(2026, 1, 18, 22, 52, 52, 466000, tzinfo=UTC),
        time_zone="America/New_York",
    )

    assert "2026-01-18 / 17:52:52.466 UTC-05:00" in html


@pytest.mark.parametrize("time_zone", ["UTC-24:00", "UTC+02:60", "Not/A_Zone"])
def test_render_health_report_rejects_invalid_time_zone(time_zone: str) -> None:
    report = HealthReport(status="ok", checks=[], duration_ms=0)

    with pytest.raises(ValueError):
        render_health_report_page(report, time_zone=time_zone)


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

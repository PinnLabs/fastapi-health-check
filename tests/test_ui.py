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
    assert "Total duration" in html
    assert "15.68 ms" in html


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
    assert "800 µs" in html


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
    assert "2.35 s" in html
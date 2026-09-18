from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta, timezone
from functools import lru_cache
from html import escape
from importlib.resources import files
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi_health_check.models import HealthCheckResult, HealthReport

_ASSETS = files("fastapi_health_check.assets")
_UTC_OFFSET = re.compile(r"UTC([+-])(\d{2}):(\d{2})\Z")


def _resolve_time_zone(name: str) -> ZoneInfo | timezone:
    if name == "UTC":
        return UTC

    match = _UTC_OFFSET.fullmatch(name)
    if match:
        sign, hours, minutes = match.groups()
        if int(hours) > 23 or int(minutes) > 59:
            raise ValueError(f"Invalid time zone offset: {name}")
        offset = timedelta(hours=int(hours), minutes=int(minutes))
        return timezone(offset if sign == "+" else -offset)

    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"Unknown time zone: {name}") from exc


def _time_zone_label(timestamp: datetime) -> str:
    offset = timestamp.utcoffset()
    if offset == timedelta(0):
        return "UTC"
    assert offset is not None
    sign = "+" if offset > timedelta(0) else "-"
    total_minutes = abs(int(offset.total_seconds() // 60))
    hours, minutes = divmod(total_minutes, 60)
    return f"UTC{sign}{hours:02d}:{minutes:02d}"


@lru_cache(maxsize=1)
def _html_template() -> str:
    return (_ASSETS / "health-report.html").read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def _css_styles() -> str:
    return (_ASSETS / "health-report.css").read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def _js_script() -> str:
    return (_ASSETS / "health-report.js").read_text(encoding="utf-8")


def render_health_report_page(
    report: HealthReport,
    *,
    title: str = "FastAPI Health Check",
    endpoint: str = "/ht",
    liveness_endpoint: str = "/health/live",
    readiness_endpoint: str = "/health/ready",
    generated_at: datetime | None = None,
    time_zone: str = "UTC",
) -> str:
    """Render a self-contained diagnostic report for a health-check run."""
    timestamp = generated_at or datetime.now(UTC)
    timestamp = timestamp.astimezone(_resolve_time_zone(time_zone))
    zone_label = _time_zone_label(timestamp)
    checked_at = timestamp.strftime("%H:%M:%S.%f")[:-3] + f" {zone_label}"
    checks_markup = (
        "\n".join(
            _render_check_row(check, index=index, checked_at=checked_at)
            for index, check in enumerate(report.checks)
        )
        or _render_empty_state()
    )

    replacements = {
        "{{ title }}": escape(title),
        "{{ styles }}": _css_styles(),
        "{{ script }}": _js_script(),
        "{{ endpoint_href }}": escape(endpoint, quote=True),
        "{{ liveness_href }}": escape(liveness_endpoint, quote=True),
        "{{ readiness_href }}": escape(readiness_endpoint, quote=True),
        "{{ diagnostic_datetime }}": timestamp.isoformat(timespec="milliseconds"),
        "{{ time_zone }}": escape(time_zone, quote=True),
        "{{ diagnostic_timestamp }}": timestamp.strftime("%Y-%m-%d / %H:%M:%S.%f")[:-3]
        + f" {zone_label}",
        "{{ checks_markup }}": checks_markup,
    }

    html = _html_template()
    for marker, value in replacements.items():
        html = html.replace(marker, value)

    return html


def _format_duration(duration_ms: float) -> str:
    if duration_ms < 1:
        return f"{duration_ms * 1000:.0f} µs"
    if duration_ms < 1000:
        return f"{duration_ms:.2f} ms"
    return f"{duration_ms / 1000:.2f} s"


def _render_check_row(check: HealthCheckResult, *, index: int, checked_at: str) -> str:
    status_class = "healthy" if check.status == "ok" else "unhealthy"
    status_label = "healthy" if check.status == "ok" else "unhealthy"
    message = (
        escape(check.message) if check.message else "No diagnostic message returned"
    )
    detail_label = "message" if check.status == "ok" else "error"
    detail_value_class = " trace__value--error" if check.status == "fail" else ""
    is_last_branch = "└─"

    return f"""          <details class="check-record" role="rowgroup" data-check-index="{index}">
            <summary class="check-row" role="row">
              <span class="check-name" role="cell">
                <span class="disclosure-mark" aria-hidden="true"></span>
                <span class="check-name__text">{escape(check.name)}</span>
              </span>
              <span class="status {status_class}" role="cell" data-status>
                <span class="status__mark" aria-hidden="true">●</span><span data-status-label>{status_label}</span>
              </span>
              <span class="latency" role="cell"><span class="cell-label">Latency</span><span data-latency>{_format_duration(check.duration_ms)}</span></span>
              <span class="check-message" role="cell"><span class="cell-label">Message</span><span data-message>{message}</span></span>
            </summary>
            <div class="check-detail" id="check-detail-{index}">
              <div class="trace" aria-label="Technical details for {escape(check.name)}">
                <div class="trace__line"><span class="trace__branch">├─</span><span class="trace__key">type</span><span class="trace__value">registry_check</span></div>
                <div class="trace__line"><span class="trace__branch">├─</span><span class="trace__key">identifier</span><span class="trace__value">{escape(check.name)}</span></div>
                <div class="trace__line"><span class="trace__branch">├─</span><span class="trace__key">duration</span><span class="trace__value" data-detail-duration>{_format_duration(check.duration_ms)}</span></div>
                <div class="trace__line"><span class="trace__branch">├─</span><span class="trace__key">checked_at</span><span class="trace__value" data-detail-checked-at>{checked_at}</span></div>
                <div class="trace__line"><span class="trace__branch">{is_last_branch}</span><span class="trace__key" data-detail-message-key>{detail_label}</span><span class="trace__value{detail_value_class}" data-detail-message>{message}</span></div>
              </div>
            </div>
          </details>"""


def _render_empty_state() -> str:
    return '          <div class="empty-state"><span>No health checks are currently registered</span></div>'

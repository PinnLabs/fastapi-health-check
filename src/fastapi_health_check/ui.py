from __future__ import annotations

import base64
from functools import lru_cache
from html import escape
from importlib.resources import files

from fastapi_health_check.models import HealthCheckResult, HealthReport

_ASSETS = files("fastapi_health_check.assets")


@lru_cache(maxsize=1)
def _html_template() -> str:
    return (_ASSETS / "health-report.html").read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def _css_styles() -> str:
    return (_ASSETS / "health-report.css").read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def _logo_b64() -> str:
    try:
        return base64.b64encode((_ASSETS / "pinnlabs-logo.png").read_bytes()).decode("ascii")
    except OSError:
        return ""


def render_health_report_page(report: HealthReport, *, title: str = "FastAPI Health Check") -> str:
    summary_label = "Healthy" if report.is_healthy else "Issues detected"
    summary_class = "ok" if report.is_healthy else "fail"
    checks_markup = "\n".join(_render_check_card(check) for check in report.checks) or _render_empty_state()

    replacements = {
        "{{ title }}": escape(title),
        "{{ styles }}": _css_styles(),
        "{{ summary_class }}": summary_class,
        "{{ summary_label }}": escape(summary_label),
        "{{ checks_count }}": str(len(report.checks)),
        "{{ total_duration }}": (
            _format_duration(report.duration_ms)
            if report.duration_ms is not None
            else "Unavailable"
        ),
        "{{ checks_markup }}": checks_markup,
        "{{ powered_by_markup }}": _render_powered_by(),
    }

    html = _html_template()
    for marker, value in replacements.items():
        html = html.replace(marker, value)

    return html


def _render_powered_by() -> str:
    b64 = _logo_b64()
    img = f'<img src="data:image/png;base64,{b64}" alt="PinnLabs" class="powered-by-logo" />' if b64 else ""
    return f"""    <footer class="powered-by">
      <span>Powered by</span>
      {img}
    </footer>"""

def _format_duration(duration_ms: float) -> str:
    if duration_ms < 1:
        return f"{duration_ms * 1000:.0f} µs"
    if duration_ms < 1000:
        return f"{duration_ms:.2f} ms"
    return f"{duration_ms / 1000:.2f} s"


def _render_check_card(check: HealthCheckResult) -> str:
    message = escape(check.message) if check.message else "No additional details."
    return f"""        <article class="check-card">
          <div class="check-header">
            <h2 class="check-name">{escape(check.name)}</h2>
            <div class="check-meta">
              <div class="badge {check.status}">{escape(check.status.upper())}</div>
              <span class="duration">{_format_duration(check.duration_ms)}</span>
            </div>
          </div>
          <p class="message">{message}</p>
        </article>"""


def _render_empty_state() -> str:
    return '        <div class="empty">No health checks are currently registered.</div>'
